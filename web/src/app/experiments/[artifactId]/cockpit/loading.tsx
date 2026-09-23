import { AppHeader } from "@/components/AppHeader";

export default function ScientificCockpitLoading() {
  return (
    <div className="app-shell cockpit-shell">
      <AppHeader />
      <main className="cockpit-route" aria-live="polite">
        <div className="cockpit-loading-heading">
          <p className="eyebrow">SCIENTIFIC COCKPIT / READ ONLY</p>
          <h1>Reading the persisted experiment…</h1>
          <p>Validating its timeline and the local MaleCNS source layers.</p>
        </div>
        <div className="cockpit-loading-grid" aria-hidden="true">
          <span>WORLD / STIMULUS</span>
          <span>MALECNS STRUCTURE</span>
          <span>RUN / SELECTED NEURON</span>
          <span>EXPERIMENT TELEMETRY</span>
          <span>EVENT TIMELINE</span>
        </div>
        <div className="cockpit-loading-transport" aria-hidden="true">PLAYBACK / TIMELINE</div>
      </main>
    </div>
  );
}
