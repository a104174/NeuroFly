import { AppHeader } from "@/components/AppHeader";

export default function Loading() {
  return (
    <div className="app-shell">
      <AppHeader />
      <main className="main-content main-content-wide">
        <div className="state-message" aria-live="polite">
          <p className="eyebrow">READ-ONLY CATALOGUE</p>
          <h1>Loading experiments…</h1>
          <p className="state-detail">Reading completed artifacts from the Phase 4B API.</p>
        </div>
      </main>
    </div>
  );
}
