import { useState } from "react"
import "./index.css"
import HomePage from "./pages/HomePage"
import SearchPage from "./pages/SearchPage"
import CitePage from "./pages/CitePage"

function Nav({ page, setPage }) {
  return (
    <nav>
      <div className="nav-brand">
        <div className="nav-brand-dot" />
        SourceBot
      </div>
      <div className="nav-links">
        <a className={`nav-link ${page === "home" ? "active" : ""}`}
          onClick={() => setPage("home")}>Home</a>
        <a className={`nav-link ${page === "search" ? "active" : ""}`}
          onClick={() => setPage("search")}>Quick Search</a>
        <a className={`nav-link ${page === "cite" ? "active" : ""}`}
          onClick={() => setPage("cite")}>Generate Citations</a>
      </div>
    </nav>
  )
}

export default function App() {
  const [page, setPage] = useState("home")

  return (
    <div className="app">
      <Nav page={page} setPage={setPage} />
      <main>
        {page === "home"   && <HomePage setPage={setPage} />}
        {page === "search" && <SearchPage />}
        {page === "cite"   && <CitePage />}
      </main>
      <footer>An Ian Patterson Production</footer>
    </div>
  )
}