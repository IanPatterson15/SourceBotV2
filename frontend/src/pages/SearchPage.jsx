import { useState } from "react"

const API = "http://127.0.0.1:8000"

function Spinner() {
  return (
    <div className="spinner">
      <div className="spinner-dot" />
      <div className="spinner-dot" />
      <div className="spinner-dot" />
      Searching through sources...
    </div>
  )
}

function ResultCard({ result, index }) {
  const [copied, setCopied] = useState(false)

  function handleCopy() {
    navigator.clipboard.writeText(result.apa).then(() => {
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    })
  }

  return (
    <div className="result-card fade-in">
      <div className="result-title">{result.title}</div>
      <div className="result-meta">{result.authors} · {result.year}</div>

      <div className="result-label">Why it's relevant</div>
      <div className="result-relevance">{result.relevance}</div>

      <div className="result-label">Relevant quotes</div>
      {result.quotes.map((q, i) => (
        <div className="result-quote" key={i}>"{q}"</div>
      ))}

      <div className="result-label" style={{ marginTop: "18px" }}>Source</div>
      {result.link
        ? <div className="result-link"><a href={result.link} target="_blank" rel="noreferrer">↗ Read the full paper</a></div>
        : <div className="result-meta">No link available</div>
      }

      <div className="result-label" style={{ marginTop: "18px" }}>APA Citation</div>
      <div className="result-citation-block">
        <div className="result-citation-text">{result.apa}</div>
        <button className={`copy-btn ${copied ? "copied" : ""}`} onClick={handleCopy}>
          {copied ? "✓ Copied" : "Copy"}
        </button>
      </div>
    </div>
  )
}

export default function SearchPage() {
  const [query, setQuery] = useState("")
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")
  const [history, setHistory] = useState([])

  async function handleSearch() {
    if (!query.trim()) return
    setLoading(true)
    setError("")
    setResults([])
    if (!history.includes(query)) {
      setHistory(prev => [query, ...prev])
    }
    try {
      const res = await fetch(`${API}/search`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query })
      })
      const data = await res.json()
      setResults(data.results)
    } catch (e) {
      setError("Something went wrong. Is the backend running?")
    }
    setLoading(false)
  }

  function handleKeyDown(e) {
    if (e.key === "Enter" && e.metaKey) handleSearch()
  }

  return (
    <div className="search-page">
      <div className="search-sidebar">
        <div className="sidebar-title">Recent Searches</div>
        {history.length === 0
          ? <div className="sidebar-empty">Your searches will appear here as you explore.</div>
          : history.map((q, i) => (
              <div className="sidebar-item" key={i} onClick={() => setQuery(q)}>{q}</div>
            ))
        }
      </div>

      <div className="search-main">
        <div className="page-tag">Quick Search</div>
        <h1 className="search-title">What are you looking for?</h1>
        <p className="search-subtitle">Describe your research argument or question — the more specific, the better.</p>

        <textarea
          className="search-textarea"
          placeholder="e.g. An argument that raising the minimum wage does not significantly increase unemployment..."
          value={query}
          onChange={e => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
        />

        <div className="search-actions">
          <button className="btn-primary" onClick={handleSearch} disabled={loading}>
            Search Papers
          </button>
        </div>

        {error && <div className="error-msg">{error}</div>}
        {loading && <Spinner />}
        {results.map((r, i) => <ResultCard key={i} result={r} index={i} />)}
      </div>
    </div>
  )
}