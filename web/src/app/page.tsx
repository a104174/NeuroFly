import { AppHeader } from "@/components/AppHeader";
import { ExperimentList } from "@/components/ExperimentList";
import { StateMessage } from "@/components/StateMessage";
import {
  listExperiments,
  NeuroflyApiError,
  type ExperimentSummary,
} from "@/lib/neuroflyClient";

export const dynamic = "force-dynamic";

export default async function HomePage() {
  let experiments: ExperimentSummary[] | null = null;
  let requestError: unknown = null;
  try {
    experiments = await listExperiments();
  } catch (error) {
    requestError = error;
  }
  if (requestError) {
    const detail =
      requestError instanceof NeuroflyApiError
        ? requestError.message
        : "The experiment API could not be reached.";
    return (
      <div className="app-shell">
        <AppHeader />
        <main className="main-content main-content-wide">
          <StateMessage
            eyebrow="API UNAVAILABLE"
            title="The catalogue could not load."
            detail={detail}
            tone="error"
          />
        </main>
      </div>
    );
  }
  if (!experiments || experiments.length === 0) {
    return (
      <div className="app-shell">
        <AppHeader />
        <main className="main-content main-content-wide">
          <StateMessage
            eyebrow="NO COMPLETED RUNS"
            title="The catalogue is empty."
            detail="No completed experiment artifacts are available through the configured read-only API yet."
          />
        </main>
      </div>
    );
  }
  return (
    <div className="app-shell">
      <AppHeader />
      <div className="workspace">
        <aside className="catalogue">
          <div className="catalogue-inner">
            <p className="eyebrow">NEUROFLY / PHASE 5A</p>
            <h1 className="catalogue-title">Model experiments</h1>
            <p className="catalogue-copy">
              Browse deterministic runs persisted by the scientific core.
              Nothing on this page starts a simulation.
            </p>
            <ExperimentList experiments={experiments} />
          </div>
        </aside>
        <main className="main-content main-content-wide">
          <section className="hero-panel">
            <div>
              <p className="eyebrow">READ-ONLY WORKSPACE</p>
              <h1>Observe the model.</h1>
              <p className="hero-copy">
                Select a completed run to inspect its provenance, pathway
                output, and persisted neural timeline.
              </p>
            </div>
            <div className="validation-flag">
              <span className="status-dot" aria-hidden="true" />
              <span>
                <strong>Empirical validation</strong>
                <small>Not evaluated</small>
              </span>
            </div>
          </section>
          <section className="section-block">
            <div className="section-heading">
              <p className="eyebrow">BROWSER BOUNDARY</p>
              <h2>Choose a run from the catalogue.</h2>
            </div>
            <p className="subtle-note">
              The browser consumes the Phase 4B HTTP contract only. It does
              not access Python objects, artifact paths, or simulator state.
            </p>
          </section>
        </main>
      </div>
    </div>
  );
}
