import { SiteHeader } from "@/components/site/SiteChrome";

export default function Loading() {
  return (
    <div className="app-shell">
      <SiteHeader />
      <main id="main-content" tabIndex={-1} className="main-content main-content-wide">
        <div className="state-message" role="status" aria-live="polite" aria-busy="true">
          <p className="eyebrow">READ-ONLY CATALOGUE</p>
          <h1>Loading scientific data…</h1>
          <p className="state-detail">Reading the configured backend. No substitute data are displayed.</p>
        </div>
      </main>
    </div>
  );
}
