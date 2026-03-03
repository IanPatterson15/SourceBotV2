import { useState } from "react"

const API = "http://127.0.0.1:8000"

export default function CitePage() {
  const [fetchInput, setFetchInput] = useState("")
  const [fetchLoading, setFetchLoading] = useState(false)
  const [fetchError, setFetchError] = useState("")
  const [fetchSuccess, setFetchSuccess] = useState(false)

  const [citeFormat, setCiteFormat] = useState("APA")
  const [sourceType, setSourceType] = useState("Journal Article")

  const [title, setTitle] = useState("")
  const [authors, setAuthors] = useState("")
  const [year, setYear] = useState("")
  const [doi, setDoi] = useState("")
  const [journal, setJournal] = useState("")
  const [volume, setVolume] = useState("")
  const [issue, setIssue] = useState("")
  const [pages, setPages] = useState("")
  const [url, setUrl] = useState("")
  const [siteName, setSiteName] = useState("")
  const [publishDate, setPublishDate] = useState("")
  const [accessDate, setAccessDate] = useState("")

  const [citation, setCitation] = useState("")
  const [genLoading, setGenLoading] = useState(false)
  const [genError, setGenError] = useState("")
  const [copied, setCopied] = useState(false)

  async function handleFetch() {
    if (!fetchInput.trim()) return
    setFetchLoading(true)
    setFetchError("")
    setFetchSuccess(false)
    try {
      const res = await fetch(`${API}/fetch`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ input: fetchInput })
      })
      const data = await res.json()
      if (data.success) {
        const d = data.data
        setTitle(d.title || "")
        setAuthors(d.authors || "")
        setYear(d.year || "")
        setDoi(d.doi || "")
        setJournal(d.journal || "")
        setVolume(d.volume || "")
        setIssue(d.issue || "")
        setPages(d.pages || "")
        setUrl(d.url || "")
        setSiteName(d.site_name || "")
        setPublishDate(d.publish_date || "")
        if (d.source_type === "website") setSourceType("Website")
        setFetchSuccess(true)
        setCitation("")
      } else {
        setFetchError(data.error || "Could not fetch metadata.")
      }
    } catch (e) {
      setFetchError("Something went wrong. Is the backend running?")
    }
    setFetchLoading(false)
  }

  async function handleGenerate() {
    setGenLoading(true)
    setGenError("")
    setCitation("")
    try {
      const res = await fetch(`${API}/cite`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          format: citeFormat,
          source_type: sourceType === "Website" ? "website" : "journal",
          title, authors, year, doi, journal, volume, issue, pages,
          url, site_name: siteName, publish_date: publishDate, access_date: accessDate
        })
      })
      const data = await res.json()
      setCitation(data.citation)
    } catch (e) {
      setGenError("Something went wrong. Is the backend running?")
    }
    setGenLoading(false)
  }

  function handleClear() {
    setTitle(""); setAuthors(""); setYear(""); setDoi("")
    setJournal(""); setVolume(""); setIssue(""); setPages("")
    setUrl(""); setSiteName(""); setPublishDate(""); setAccessDate("")
    setCitation(""); setFetchInput(""); setFetchSuccess(false); setFetchError("")
  }

  function handleCopy() {
    navigator.clipboard.writeText(citation).then(() => {
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    })
  }

  const isWebsite = citeFormat === "MLA" && sourceType === "Website"

  return (
    <div className="cite-page">
      <h1 className="cite-title fade-in">Generate Citations</h1>
      <p className="cite-subtitle fade-in">Paste a link or DOI to auto-fill, or enter details manually.</p>

      {/* AUTO-FILL */}
      <span className="section-label">Auto-Fill from URL or DOI</span>
      <div className="fetch-row">
        <input
          className="text-input"
          placeholder="e.g. https://doi.org/10.1257/aer.20180975  or  https://www.brookings.edu/articles/..."
          value={fetchInput}
          onChange={e => setFetchInput(e.target.value)}
          onKeyDown={e => e.key === "Enter" && handleFetch()}
        />
        <button className="btn-primary" onClick={handleFetch} disabled={fetchLoading}>
          {fetchLoading ? "Fetching..." : "Fetch"}
        </button>
      </div>
      {fetchError   && <div className="error-msg">{fetchError}</div>}
      {fetchSuccess && <div className="success-msg">✓ Metadata fetched — fields have been pre-filled below.</div>}

      {/* FORMAT + SOURCE TYPE */}
      <div className="two-col" style={{ marginTop: "24px" }}>
        <div className="field-group">
          <label className="field-label">Citation Format</label>
          <select className="select-input" value={citeFormat} onChange={e => setCiteFormat(e.target.value)}>
            <option>APA</option>
            <option>MLA</option>
          </select>
        </div>
        <div className="field-group">
          <label className="field-label">Source Type</label>
          <select className="select-input" value={sourceType}
            onChange={e => setSourceType(e.target.value)}
            disabled={citeFormat === "APA"}>
            <option>Journal Article</option>
            {citeFormat === "MLA" && <option>Website</option>}
          </select>
        </div>
      </div>

      {/* SOURCE DETAILS */}
      <span className="section-label">Source Details</span>

      <div className="field-group">
        <label className="field-label">Title</label>
        <input className="text-input" placeholder="e.g. The Effects of Minimum Wage on Employment"
          value={title} onChange={e => setTitle(e.target.value)} />
      </div>

      <div className="field-group">
        <label className="field-label">Authors</label>
        <input className="text-input" placeholder="e.g. John Smith, Jane Doe  (comma-separated, First Last format)"
          value={authors} onChange={e => setAuthors(e.target.value)} />
      </div>

      {!isWebsite && (
        <>
          <div className="two-col">
            <div className="field-group">
              <label className="field-label">Year</label>
              <input className="text-input" placeholder="e.g. 2021"
                value={year} onChange={e => setYear(e.target.value)} />
            </div>
            <div className="field-group">
              <label className="field-label">DOI</label>
              <input className="text-input" placeholder="e.g. 10.1000/xyz123"
                value={doi} onChange={e => setDoi(e.target.value)} />
            </div>
          </div>

          {citeFormat === "MLA" && (
            <>
              <span className="section-label">Journal Details</span>
              <div className="field-group">
                <label className="field-label">Journal Name</label>
                <input className="text-input" placeholder="e.g. Journal of Economic Perspectives"
                  value={journal} onChange={e => setJournal(e.target.value)} />
              </div>
              <div className="three-col">
                <div className="field-group">
                  <label className="field-label">Volume</label>
                  <input className="text-input" placeholder="e.g. 12"
                    value={volume} onChange={e => setVolume(e.target.value)} />
                </div>
                <div className="field-group">
                  <label className="field-label">Issue</label>
                  <input className="text-input" placeholder="e.g. 3"
                    value={issue} onChange={e => setIssue(e.target.value)} />
                </div>
                <div className="field-group">
                  <label className="field-label">Pages</label>
                  <input className="text-input" placeholder="e.g. 45-67"
                    value={pages} onChange={e => setPages(e.target.value)} />
                </div>
              </div>
            </>
          )}
        </>
      )}

      {isWebsite && (
        <>
          <span className="section-label">Website Details</span>
          <div className="two-col">
            <div className="field-group">
              <label className="field-label">Site Name</label>
              <input className="text-input" placeholder="e.g. Brookings Institution"
                value={siteName} onChange={e => setSiteName(e.target.value)} />
            </div>
            <div className="field-group">
              <label className="field-label">URL</label>
              <input className="text-input" placeholder="e.g. https://www.brookings.edu/..."
                value={url} onChange={e => setUrl(e.target.value)} />
            </div>
          </div>
          <div className="two-col">
            <div className="field-group">
              <label className="field-label">Publish Date</label>
              <input className="text-input" placeholder="e.g. 14 Mar. 2023"
                value={publishDate} onChange={e => setPublishDate(e.target.value)} />
            </div>
            <div className="field-group">
              <label className="field-label">Access Date</label>
              <input className="text-input" placeholder="e.g. 1 Jan. 2024"
                value={accessDate} onChange={e => setAccessDate(e.target.value)} />
            </div>
          </div>
        </>
      )}

      {/* BUTTONS */}
      <div style={{ display: "flex", gap: "12px", marginTop: "24px" }}>
        <button className="btn-primary" onClick={handleGenerate} disabled={genLoading}>
          {genLoading ? "Generating..." : "Generate Citation"}
        </button>
        <button className="btn-secondary" onClick={handleClear}>Clear</button>
      </div>

      {genError && <div className="error-msg">{genError}</div>}

      {/* RESULT */}
      {citation && (
        <div className="citation-result fade-in">
          <div className="citation-result-text">{citation}</div>
          <button className={`copy-btn ${copied ? "copied" : ""}`} onClick={handleCopy}>
            {copied ? "✓ Copied" : "Copy"}
          </button>
        </div>
      )}
    </div>
  )
}