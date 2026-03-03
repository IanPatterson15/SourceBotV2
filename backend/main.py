import os
from concurrent.futures import ThreadPoolExecutor
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import requests
from urllib.parse import urlparse
import re

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

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

frontend_dist = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
if os.path.exists(frontend_dist):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")

class SearchRequest(BaseModel):
    query: str

class CitationRequest(BaseModel):
    format: str
    source_type: str
    title: str
    authors: str
    year: str
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

def get_embedding(text):
    response = client.embeddings.create(input=text, model="text-embedding-3-small")
    return response.data[0].embedding

def analyze_paper(abstract, query):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": f"""You are a research assistant. A student is writing a paper with this argument or question: "{query}"

Here is an abstract from an academic paper:
{abstract}

Please provide:
1. A 2-3 sentence explanation of why this paper is relevant to the student's argument
2. 2-3 direct quotes from the abstract that would be useful

Format your response exactly like this:
RELEVANCE: [your explanation]
QUOTE1: [first quote]
QUOTE2: [second quote]
QUOTE3: [third quote]"""}],
        max_tokens=500
    )
    return response.choices[0].message.content

def parse_analysis(analysis):
    relevance = ""
    quotes = []
    for line in analysis.split('\n'):
        if line.startswith('RELEVANCE:'):
            relevance = line.replace('RELEVANCE:', '').strip()
        elif line.startswith('QUOTE'):
            quote = re.sub(r'^QUOTE\d+:\s*', '', line).strip()
            if quote:
                quotes.append(quote)
    return relevance, quotes

def format_apa(title, authors, year, doi):
    author_list = [a.strip() for a in authors.split(',') if a.strip()]
    formatted = []
    for a in author_list:
        parts = a.strip().split()
        if len(parts) >= 2:
            last = parts[-1]
            initials = ' '.join([p[0] + '.' for p in parts[:-1]])
            formatted.append(f"{last}, {initials}")
        else:
            formatted.append(a)
    if len(formatted) == 0: author_str = "Unknown"
    elif len(formatted) == 1: author_str = formatted[0]
    elif len(formatted) <= 20: author_str = ', '.join(formatted[:-1]) + ', & ' + formatted[-1]
    else: author_str = ', '.join(formatted[:19]) + ', ... ' + formatted[-1]
    doi_clean = doi.replace('https://doi.org/', '') if doi else ''
    doi_str = f" https://doi.org/{doi_clean}" if doi_clean else ""
    return f"{author_str} ({year}). {title}.{doi_str}"

def format_mla_journal(title, authors, year, journal, volume, issue, pages, doi):
    author_list = [a.strip() for a in authors.split(',') if a.strip()]
    if len(author_list) == 0: author_str = "Unknown"
    elif len(author_list) == 1:
        parts = author_list[0].split()
        author_str = (parts[-1] + ', ' + ' '.join(parts[:-1])) if len(parts) >= 2 else author_list[0]
    else:
        parts = author_list[0].split()
        first = (parts[-1] + ', ' + ' '.join(parts[:-1])) if len(parts) >= 2 else author_list[0]
        author_str = first + ', et al'
    vol_issue = f", vol. {volume}" if volume else ""
    if issue: vol_issue += f", no. {issue}"
    pages_str = f", pp. {pages}" if pages else ""
    doi_clean = doi.replace('https://doi.org/', '') if doi else ''
    doi_str = f", https://doi.org/{doi_clean}" if doi_clean else ""
    journal_str = f" {journal}" if journal else ""
    return f'{author_str}. "{title}."{journal_str}{vol_issue}, {year}{pages_str}{doi_str}.'

def format_mla_website(title, authors, site_name, publish_date, access_date, url):
    author_list = [a.strip() for a in authors.split(',') if a.strip()]
    if len(author_list) == 0: author_str = ""
    elif len(author_list) == 1:
        parts = author_list[0].split()
        author_str = (parts[-1] + ', ' + ' '.join(parts[:-1]) + '. ') if len(parts) >= 2 else author_list[0] + '. '
    else:
        parts = author_list[0].split()
        first = (parts[-1] + ', ' + ' '.join(parts[:-1])) if len(parts) >= 2 else author_list[0]
        author_str = first + ', et al. '
    site_str = f" {site_name}," if site_name else ""
    pub_str  = f" {publish_date}," if publish_date else ""
    url_str  = f" {url}." if url else ""
    acc_str  = f" Accessed {access_date}." if access_date else ""
    return f'{author_str}"{title}."{site_str}{pub_str}{url_str}{acc_str}'

def fetch_metadata_from_doi(doi):
    doi_clean = doi.replace('https://doi.org/', '').replace('http://doi.org/', '')
    url = f"https://api.crossref.org/works/{doi_clean}"
    headers = {"User-Agent": "SourceBot/1.0 (mailto:sourcebot@school.edu)"}
    r = requests.get(url, headers=headers, timeout=10)
    r.raise_for_status()
    data = r.json()["message"]
    authors_raw = data.get("author", [])
    authors = ', '.join([f"{a.get('given','')} {a.get('family','')}".strip() for a in authors_raw])
    date_parts = data.get("published-print", data.get("published-online", {})).get("date-parts", [[""]])
    year = str(date_parts[0][0]) if date_parts and date_parts[0] else ""
    return {
        "title": data.get("title", [""])[0], "authors": authors, "year": year,
        "doi": doi_clean, "journal": data.get("container-title", [""])[0],
        "volume": data.get("volume", ""), "issue": data.get("issue", ""),
        "pages": data.get("page", ""), "source_type": "journal"
    }

def fetch_metadata_from_url(url):
    headers = {"User-Agent": "Mozilla/5.0 (compatible; SourceBot/1.0)"}
    r = requests.get(url, headers=headers, timeout=10)
    r.raise_for_status()
    html = r.text
    def meta(name):
        for pattern in [
            f'<meta name="{name}" content="([^"]+)"',
            f'<meta property="{name}" content="([^"]+)"',
            f'<meta name=\'{name}\' content=\'([^\']+)\'',
        ]:
            m = re.search(pattern, html, re.IGNORECASE)
            if m: return m.group(1)
        return ""
    title = meta("og:title") or meta("twitter:title") or meta("title") or ""
    if not title:
        m = re.search(r'<title>([^<]+)</title>', html, re.IGNORECASE)
        if m: title = m.group(1).strip()
    author    = meta("author") or meta("article:author") or ""
    site_name = meta("og:site_name") or urlparse(url).netloc.replace('www.', '')
    pub_date  = meta("article:published_time") or meta("pubdate") or ""
    if pub_date: pub_date = pub_date[:10]
    return {"title": title, "authors": author, "url": url,
            "site_name": site_name, "publish_date": pub_date, "source_type": "website"}

@app.post("/search")
def search(req: SearchRequest):
    embedding = get_embedding(req.query)
    hits = qdrant.query_points(collection_name=COLLECTION_NAME, query=embedding, limit=5, with_payload=True).points
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
        link    = f"https://doi.org/{doi.replace('https://doi.org/','')}" if doi else None
        return {"title": title, "authors": authors, "year": year,
                "relevance": relevance, "quotes": quotes, "apa": apa, "link": link}
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(process_hit, hits))
    return {"results": results}

@app.post("/cite")
def cite(req: CitationRequest):
    if req.format == "APA":
        citation = format_apa(req.title, req.authors, req.year, req.doi)
    elif req.format == "MLA" and req.source_type == "website":
        citation = format_mla_website(req.title, req.authors, req.site_name, req.publish_date, req.access_date, req.url)
    else:
        citation = format_mla_journal(req.title, req.authors, req.year, req.journal, req.volume, req.issue, req.pages, req.doi)
    return {"citation": citation}

@app.post("/fetch")
def fetch(req: FetchRequest):
    inp = req.input.strip()
    try:
        if "doi.org" in inp or re.match(r'^10\.\d{4,}/', inp):
            data = fetch_metadata_from_doi(inp)
        else:
            data = fetch_metadata_from_url(inp)
        return {"success": True, "data": data}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/")
def serve_root():
    index = os.path.join(frontend_dist, "index.html")
    if os.path.exists(index):
        return FileResponse(index)
    return {"status": "SourceBot API running"}

@app.get("/{catchall:path}")
def serve_app(catchall: str):
    index = os.path.join(frontend_dist, "index.html")
    if os.path.exists(index):
        return FileResponse(index)
    return {"status": "SourceBot API running"}