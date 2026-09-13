import Link from "next/link";

export function AppHeader() {
  return (
    <header className="app-header">
      <Link className="brand" href="/" aria-label="NeuroFly experiments home">
        <span className="brand-mark" aria-hidden="true">
          NF
        </span>
        <span>
          <span className="brand-name">NeuroFly</span>
          <span className="brand-subtitle">connectome experiment browser</span>
        </span>
      </Link>
      <nav className="header-nav" aria-label="Primary navigation">
        <Link href="/">Experiments</Link>
        <Link href="/morphology">Morphology</Link>
        <span className="header-status" aria-label="Application status">
          <span className="status-dot" aria-hidden="true" />
          <span>READ ONLY</span>
        </span>
      </nav>
    </header>
  );
}
