import { AppHeader } from "@/components/AppHeader";

export default function ExperimentLoading() {
  return (
    <div className="app-shell">
      <AppHeader />
      <main className="main-content main-content-wide">
        <div className="state-message" aria-live="polite">
          <p className="eyebrow">PERSISTED RUN</p>
          <h1>Loading experiment…</h1>
          <p className="state-detail">Reading summary and timeline telemetry. No simulation is running.</p>
        </div>
      </main>
    </div>
  );
}
