import { AppHeader } from "@/components/AppHeader";

export default function Loading() {
  return <div className="app-shell"><AppHeader/><main className="scenario-route"><p className="eyebrow">NEUROFLY / SCIENTIFIC SCENARIOS</p><div className="library-heading"><h1>Experiments, not predictions.</h1></div><section className="scientific-loading" role="status" aria-busy="true"><span className="instrument-index">CATALOG CHECK</span><h2>Loading scientific experiments</h2><p>Reading the canonical scenario catalog from the backend. No substitute experiment data are displayed.</p></section></main></div>;
}
