export default function HomePage({ setPage }) {

  const graphSvg = (
    <svg viewBox="0 0 480 420" xmlns="http://www.w3.org/2000/svg"
      style={{ width: "580px", height: "520px", opacity: 0.82, transform: "translateX(40px)" }}>
      <defs>
        <style>{`
          .nr{fill:none;stroke:#c4a35a;stroke-width:1.2}
          .nd{fill:#c4a35a}
          .ns{fill:rgba(196,163,90,0.45)}
          .eg{stroke:rgba(196,163,90,0.18);stroke-width:1;fill:none}
          .eb{stroke:rgba(196,163,90,0.38);stroke-width:1.2;fill:none}
          @keyframes dI{from{stroke-dashoffset:1}to{stroke-dashoffset:0}}
          @keyframes fN{from{opacity:0;transform:scale(0.4)}to{opacity:1;transform:scale(1)}}
          .e1{stroke-dasharray:1;stroke-dashoffset:1;animation:dI 1.2s ease 0.2s forwards}
          .e2{stroke-dasharray:1;stroke-dashoffset:1;animation:dI 1.0s ease 0.4s forwards}
          .e3{stroke-dasharray:1;stroke-dashoffset:1;animation:dI 1.1s ease 0.3s forwards}
          .e4{stroke-dasharray:1;stroke-dashoffset:1;animation:dI 0.9s ease 0.6s forwards}
          .e5{stroke-dasharray:1;stroke-dashoffset:1;animation:dI 1.0s ease 0.5s forwards}
          .e6{stroke-dasharray:1;stroke-dashoffset:1;animation:dI 1.2s ease 0.7s forwards}
          .e7{stroke-dasharray:1;stroke-dashoffset:1;animation:dI 0.8s ease 0.8s forwards}
          .e8{stroke-dasharray:1;stroke-dashoffset:1;animation:dI 1.1s ease 0.9s forwards}
          .e9{stroke-dasharray:1;stroke-dashoffset:1;animation:dI 1.0s ease 1.0s forwards}
          .e10{stroke-dasharray:1;stroke-dashoffset:1;animation:dI 0.9s ease 1.1s forwards}
          .e11{stroke-dasharray:1;stroke-dashoffset:1;animation:dI 1.0s ease 1.2s forwards}
          .e12{stroke-dasharray:1;stroke-dashoffset:1;animation:dI 0.8s ease 1.3s forwards}
          .n1{opacity:0;transform-origin:240px 200px;animation:fN 0.5s ease 0.1s forwards}
          .n2{opacity:0;transform-origin:140px 120px;animation:fN 0.5s ease 0.3s forwards}
          .n3{opacity:0;transform-origin:340px 110px;animation:fN 0.5s ease 0.4s forwards}
          .n4{opacity:0;transform-origin:120px 280px;animation:fN 0.5s ease 0.5s forwards}
          .n5{opacity:0;transform-origin:360px 290px;animation:fN 0.5s ease 0.6s forwards}
          .n6{opacity:0;transform-origin:240px 340px;animation:fN 0.5s ease 0.7s forwards}
          .n7{opacity:0;transform-origin:70px 180px;animation:fN 0.5s ease 0.8s forwards}
          .n8{opacity:0;transform-origin:410px 190px;animation:fN 0.5s ease 0.9s forwards}
          .n9{opacity:0;transform-origin:200px 55px;animation:fN 0.5s ease 1.0s forwards}
          .n10{opacity:0;transform-origin:290px 360px;animation:fN 0.5s ease 1.1s forwards}
          .n11{opacity:0;transform-origin:170px 360px;animation:fN 0.5s ease 1.2s forwards}
          .n12{opacity:0;transform-origin:380px 60px;animation:fN 0.5s ease 1.3s forwards}
        `}</style>
        <filter id="gl">
          <feGaussianBlur stdDeviation="2.5" result="cb"/>
          <feMerge><feMergeNode in="cb"/><feMergeNode in="SourceGraphic"/></feMerge>
        </filter>
      </defs>
      <line className="eg e1" x1="240" y1="200" x2="140" y2="120" pathLength="1"/>
      <line className="eg e2" x1="240" y1="200" x2="340" y2="110" pathLength="1"/>
      <line className="eg e3" x1="240" y1="200" x2="120" y2="280" pathLength="1"/>
      <line className="eg e4" x1="240" y1="200" x2="360" y2="290" pathLength="1"/>
      <line className="eg e5" x1="240" y1="200" x2="240" y2="340" pathLength="1"/>
      <line className="eb e6" x1="140" y1="120" x2="340" y2="110" pathLength="1"/>
      <line className="eg e7" x1="140" y1="120" x2="70" y2="180" pathLength="1"/>
      <line className="eg e8" x1="140" y1="120" x2="200" y2="55" pathLength="1"/>
      <line className="eg e9" x1="340" y1="110" x2="410" y2="190" pathLength="1"/>
      <line className="eg e10" x1="340" y1="110" x2="380" y2="60" pathLength="1"/>
      <line className="eg e11" x1="120" y1="280" x2="240" y2="340" pathLength="1"/>
      <line className="eg e12" x1="360" y1="290" x2="240" y2="340" pathLength="1"/>
      <line className="eg e7" x1="70" y1="180" x2="120" y2="280" pathLength="1"/>
      <line className="eg e9" x1="410" y1="190" x2="360" y2="290" pathLength="1"/>
      <line className="eg e12" x1="240" y1="340" x2="290" y2="360" pathLength="1"/>
      <line className="eg e11" x1="240" y1="340" x2="170" y2="360" pathLength="1"/>
      <g className="n1" filter="url(#gl)"><circle cx="240" cy="200" r="14" className="nr"/><circle cx="240" cy="200" r="5" className="nd"/></g>
      <g className="n2" filter="url(#gl)"><circle cx="140" cy="120" r="10" className="nr"/><circle cx="140" cy="120" r="4" className="nd"/></g>
      <g className="n3" filter="url(#gl)"><circle cx="340" cy="110" r="10" className="nr"/><circle cx="340" cy="110" r="4" className="nd"/></g>
      <g className="n4"><circle cx="120" cy="280" r="8" className="nr"/><circle cx="120" cy="280" r="3" className="nd"/></g>
      <g className="n5"><circle cx="360" cy="290" r="8" className="nr"/><circle cx="360" cy="290" r="3" className="nd"/></g>
      <g className="n6"><circle cx="240" cy="340" r="9" className="nr"/><circle cx="240" cy="340" r="3.5" className="nd"/></g>
      <g className="n7"><circle cx="70" cy="180" r="5" className="nr"/><circle cx="70" cy="180" r="2" className="ns"/></g>
      <g className="n8"><circle cx="410" cy="190" r="5" className="nr"/><circle cx="410" cy="190" r="2" className="ns"/></g>
      <g className="n9"><circle cx="200" cy="55" r="5" className="nr"/><circle cx="200" cy="55" r="2" className="ns"/></g>
      <g className="n10"><circle cx="290" cy="360" r="4" className="nr"/><circle cx="290" cy="360" r="1.5" className="ns"/></g>
      <g className="n11"><circle cx="170" cy="360" r="4" className="nr"/><circle cx="170" cy="360" r="1.5" className="ns"/></g>
      <g className="n12"><circle cx="380" cy="60" r="4" className="nr"/><circle cx="380" cy="60" r="1.5" className="ns"/></g>
    </svg>
  )

  return (
    <div className="page">
      <div className="home">
        <div className="home-content">
          <div className="home-eyebrow fade-in">AI Research Assistant</div>
          <h1 className="home-title fade-in-2">
            Research with<br /><em>precision</em><br />and clarity.
          </h1>
          <p className="home-tagline fade-in-3">
            SourceBot surfaces peer-reviewed literature and generates
            publication-ready citations — so you can focus on the argument that matters.
          </p>
          <div className="home-actions fade-in-3">
            <button className="btn-primary" onClick={() => setPage("search")}>
              Search Papers
            </button>
            <button className="btn-secondary" onClick={() => setPage("cite")}>
              Cite a Source
            </button>
          </div>
          <div className="home-stats fade-in-4">
            <div className="home-stat">
              <div className="home-stat-num">100,000+</div>
              <div className="home-stat-label">Papers Indexed</div>
            </div>
            <div className="home-stat">
              <div className="home-stat-num">APA · MLA</div>
              <div className="home-stat-label">Citation Formats</div>
            </div>
          </div>
        </div>
        <div className="home-graphic fade-in-2">
          {graphSvg}
        </div>
      </div>
    </div>
  )
}