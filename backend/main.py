import os
import re
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import requests

try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass

from openai import OpenAI
from qdrant_client import QdrantClient

# ── ENV ──────────────────────────────────────────────────────
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
QDRANT_URL     = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)
qdrant = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
COLLECTION_NAME = "economics_papers"

# ── PATHS ─────────────────────────────────────────────────────
# Dockerfile copies frontend/dist/ to /app/frontend/dist/
# and backend/ to /app/ — so __file__ is /app/main.py
# and frontend/dist is at /app/frontend/dist (same level, no "..")
BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIST = os.path.join(BASE_DIR, "frontend", "dist")
INDEX_HTML    = os.path.join(FRONTEND_DIST, "index.html")

# ── APP ───────────────────────────────────────────────────────
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static assets (JS, CSS, images) if dist folder exists
if os.path.isdir(os.path.join(FRONTEND_DIST, "assets")):
    app.mount(
        "/assets",
        StaticFiles(directory=os.path.join(FRONTEND_DIST, "assets")),
        name="assets",
    )


# ── REQUEST MODELS ────────────────────────────────────────────
class SearchRequest(BaseModel):
    query: str
    n_results: Optional[int] = 5

class CitationRequest(BaseModel):
    format: str
    source_type: str
    title: str
    authors: str
    year: Optional[str] = ""
    doi: Optional[str] = ""
    journal: Optional[str] = ""
    volume: Optional[str] = ""
    issue: Optional[str] = ""
    pages: Optional[str] = ""
    url: Optional[str] = ""
    site_name: Optional[str] = ""
    publish_date: Optional[str] = ""
    access_date: Optional[str] = ""

class FetchRequest(BaseModel):
    input: str


# ── AI HELPERS ────────────────────────────────────────────────
def get_embedding(text: str) -> list:
    response = client.embeddings.create(input=text, model="text-embedding-3-small")
    return response.data[0].embedding


def analyze_paper(abstract: str, query: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{
            "role": "user",
            "content": (
                f'You are a research assistant. A student is writing a paper with this argument or question: "{query}"\n\n'
                f"Here is an abstract from an academic paper:\n{abstract}\n\n"
                "Please provide:\n"
                "1. A 2-3 sentence explanation of why this paper is relevant to the student's argument\n"
                "2. 2-3 direct quotes from the abstract that would be useful\n\n"
                "Format your response exactly like this:\n"
                "RELEVANCE: [your explanation]\n"
                "QUOTE1: [first quote]\n"
                "QUOTE2: [second quote]\n"
                "QUOTE3: [third quote]"
            )
        }],
        max_tokens=500,
    )
    return response.choices[0].message.content


def parse_analysis(analysis: str):
    relevance = ""
    quotes = []
    for line in analysis.split("\n"):
        if line.startswith("RELEVANCE:"):
            relevance = line.replace("RELEVANCE:", "").strip()
        elif line.startswith("QUOTE"):
            quote = re.sub(r"^QUOTE\d+:\s*", "", line).strip()
            if quote:
                quotes.append(quote)
    return relevance, quotes


# ── CITATION FORMATTERS ───────────────────────────────────────
def _format_apa_authors(authors: str) -> str:
    author_list = [a.strip() for a in authors.split(",") if a.strip()]
    formatted = []
    for a in author_list:
        parts = a.split()
        if len(parts) >= 2:
            last = parts[-1]
            initials = " ".join(p[0] + "." for p in parts[:-1])
            formatted.append(f"{last}, {initials}")
        else:
            formatted.append(a)
    if not formatted:
        return "Unknown Author"
    if len(formatted) == 1:
        return formatted[0]
    if len(formatted) <= 20:
        return ", ".join(formatted[:-1]) + ", & " + formatted[-1]
    return ", ".join(formatted[:19]) + ", ... " + formatted[-1]


def format_apa(title: str, authors: str, year: str, doi: str) -> str:
    author_str = _format_apa_authors(authors)
    year_str   = f"({year})" if year else "(n.d.)"
    doi_clean  = doi.replace("https://doi.org/", "").replace("http://doi.org/", "") if doi else ""
    doi_str    = f" https://doi.org/{doi_clean}" if doi_clean else ""
    return f"{author_str} {year_str}. {title}.{doi_str}"


def format_mla_journal(
    title: str, authors: str, year: str,
    journal: str, volume: str, issue: str, pages: str, doi: str
) -> str:
    author_list = [a.strip() for a in authors.split(",") if a.strip()]
    if not author_list:
        author_str = ""
    elif len(author_list) == 1:
        parts = author_list[0].split()
        author_str = (f"{parts[-1]}, {' '.join(parts[:-1])}." if len(parts) >= 2 else author_list[0] + ".")
    else:
        parts = author_list[0].split()
        first = f"{parts[-1]}, {' '.join(parts[:-1])}" if len(parts) >= 2 else author_list[0]
        author_str = f"{first}, et al."

    title_str   = f'"{title}."'
    journal_str = f" *{journal}*," if journal else ""
    vol_str     = f" vol. {volume}," if volume else ""
    issue_str   = f" no. {issue}," if issue else ""
    year_str    = f" {year}," if year else ""
    pages_str   = f" pp. {pages}." if pages else "."
    doi_clean   = doi.replace("https://doi.org/", "").replace("http://doi.org/", "") if doi else ""
    doi_str     = f" https://doi.org/{doi_clean}." if doi_clean else ""

    return f"{author_str} {title_str}{journal_str}{vol_str}{issue_str}{year_str}{pages_str}{doi_str}".strip()


def format_mla_website(
    title: str, authors: str, site_name: str,
    publish_date: str, access_date: str, url: str
) -> str:
    author_list = [a.strip() for a in authors.split(",") if a.strip()]
    if not author_list:
        author_str = ""
    elif len(author_list) == 1:
        parts = author_list[0].split()
        author_str = (f"{parts[-1]}, {' '.join(parts[:-1])}. " if len(parts) >= 2 else author_list[0] + ". ")
    else:
        parts = author_list[0].split()
        first = f"{parts[-1]}, {' '.join(parts[:-1])}" if len(parts) >= 2 else author_list[0]
        author_str = f"{first}, et al. "

    title_str = f'"{title}."'
    site_str  = f" *{site_name}*," if site_name else ""
    pub_str   = f" {publish_date}," if publish_date else ""
    url_str   = f" {url}." if url else ""
    acc_str   = f" Accessed {access_date}." if access_date else ""

    return f"{author_str}{title_str}{site_str}{pub_str}{url_str}{acc_str}".strip()


# ── METADATA FETCHERS ─────────────────────────────────────────
def fetch_metadata_from_doi(doi: str) -> dict:
    doi_clean = re.sub(r"^https?://(dx\.)?doi\.org/", "", doi.strip())
    url = f"https://api.crossref.org/works/{doi_clean}"
    headers = {"User-Agent": "SourceBot/1.0 (mailto:sourcebot@school.edu)"}
    r = requests.get(url, headers=headers, timeout=10)
    r.raise_for_status()
    data = r.json()["message"]

    authors_raw = data.get("author", [])
    authors = ", ".join(
        f"{a.get('given', '')} {a.get('family', '')}".strip()
        for a in authors_raw
    )

    pub = data.get("published-print") or data.get("published-online") or {}
    date_parts = pub.get("date-parts", [[""]])
    year = str(date_parts[0][0]) if date_parts and date_parts[0] else ""

    return {
        "title":       data.get("title", [""])[0],
        "authors":     authors,
        "year":        year,
        "doi":         f"https://doi.org/{doi_clean}",
        "journal":     data.get("container-title", [""])[0],
        "volume":      data.get("volume", ""),
        "issue":       data.get("issue", ""),
        "pages":       data.get("page", ""),
        "source_type": "journal",
    }


def fetch_metadata_from_url(url: str) -> dict:
    headers = {"User-Agent": "Mozilla/5.0 (compatible; SourceBot/1.0)"}
    r = requests.get(url, headers=headers, timeout=10)
    r.raise_for_status()
    html = r.text

    def meta(*names):
        for name in names:
            for pattern in [
                f'<meta\\s+name="{name}"\\s+content="([^"]+)"',
                f'<meta\\s+property="{name}"\\s+content="([^"]+)"',
                f'<meta\\s+content="([^"]+)"\\s+name="{name}"',
                f'<meta\\s+content="([^"]+)"\\s+property="{name}"',
            ]:
                m = re.search(pattern, html, re.IGNORECASE)
                if m:
                    return m.group(1).strip()
        return ""

    title = meta("og:title", "twitter:title", "title")
    if not title:
        m = re.search(r"<title[^>]*>([^<]+)</title>", html, re.IGNORECASE)
        title = m.group(1).strip() if m else ""

    author    = meta("author", "article:author")
    site_name = meta("og:site_name") or urlparse(url).netloc.replace("www.", "").split(".")[0].capitalize()
    pub_date  = meta("article:published_time", "pubdate", "date")

    # Clean ISO date to readable format
    if pub_date:
        m = re.match(r"(\d{4})-(\d{2})-(\d{2})", pub_date)
        if m:
            months = ["Jan.", "Feb.", "Mar.", "Apr.", "May", "June",
                      "July", "Aug.", "Sep.", "Oct.", "Nov.", "Dec."]
            y, mo, d = m.groups()
            pub_date = f"{int(d)} {months[int(mo)-1]} {y}"

    return {
        "title":        title,
        "authors":      author,
        "url":          url,
        "site_name":    site_name,
        "publish_date": pub_date,
        "source_type":  "website",
    }


# ── API ROUTES ────────────────────────────────────────────────
@app.post("/search")
def search(req: SearchRequest):
    embedding = get_embedding(req.query)
    hits = qdrant.query_points(
        collection_name=COLLECTION_NAME,
        query=embedding,
        limit=req.n_results,
        with_payload=True,
    ).points

    def process_hit(hit):
        metadata = hit.payload
        abstract = metadata.get("text", "")
        analysis = analyze_paper(abstract, req.query)
        relevance, quotes = parse_analysis(analysis)

        doi     = metadata.get("doi", "")
        title   = metadata.get("title", "Untitled")
        authors = metadata.get("authors", "Unknown")
        year    = metadata.get("year", "")
        apa     = format_apa(title, authors, year, doi)
        doi_clean = doi.replace("https://doi.org/", "") if doi else ""
        link    = f"https://doi.org/{doi_clean}" if doi_clean else None

        return {
            "title":     title,
            "authors":   authors,
            "year":      year,
            "relevance": relevance,
            "quotes":    quotes,
            "apa":       apa,
            "link":      link,
        }

    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(process_hit, hits))

    return {"results": results}


@app.post("/cite")
def cite(req: CitationRequest):
    if req.format == "APA":
        citation = format_apa(req.title, req.authors, req.year, req.doi)
    elif req.format == "MLA" and req.source_type == "website":
        citation = format_mla_website(
            req.title, req.authors, req.site_name,
            req.publish_date, req.access_date, req.url
        )
    else:
        citation = format_mla_journal(
            req.title, req.authors, req.year,
            req.journal, req.volume, req.issue, req.pages, req.doi
        )
    return {"citation": citation}


@app.post("/fetch")
def fetch_metadata(req: FetchRequest):
    inp = req.input.strip()
    try:
        if "doi.org" in inp or re.match(r"^10\.\d{4,}/", inp):
            data = fetch_metadata_from_doi(inp)
        else:
            data = fetch_metadata_from_url(inp)
        return {"success": True, "data": data}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ── FRONTEND SERVING ──────────────────────────────────────────
@app.get("/")
def serve_root():
    if os.path.isfile(INDEX_HTML):
        return FileResponse(INDEX_HTML)
    return {"status": "SourceBot API running"}


@app.get("/{catchall:path}")
def serve_app(catchall: str):
    # Check if it's a real static file first (e.g. favicon.ico, robots.txt)
    static_file = os.path.join(FRONTEND_DIST, catchall)
    if os.path.isfile(static_file):
        return FileResponse(static_file)
    # Otherwise fall back to index.html for client-side routing
    if os.path.isfile(INDEX_HTML):
        return FileResponse(INDEX_HTML)
    return {"status": "SourceBot API running"}