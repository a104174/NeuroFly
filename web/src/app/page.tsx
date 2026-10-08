import { AppHeader } from "@/components/AppHeader";
import { ScenarioCards } from "@/components/ScenarioCards";
import { StateMessage } from "@/components/StateMessage";
import { EmptyScenarioCatalogueError, listScenarios } from "@/lib/scenarioCatalog";

export const dynamic = "force-dynamic";

export default async function HomePage() {
  let scenarios;
  try {
    scenarios = await listScenarios();
  } catch (error) {
    const empty = error instanceof EmptyScenarioCatalogueError;
    return (
      <div className="app-shell">
        <AppHeader />
        <main className="main-content main-content-wide">
          <StateMessage
            eyebrow={empty ? "NO CANONICAL SCENARIOS" : "SCENARIO API UNAVAILABLE"}
            title={empty ? "The scenario catalogue is empty." : "Scenarios could not load."}
            detail={error instanceof Error ? error.message : "Please check the backend."}
            tone={empty ? "neutral" : "error"}
          />
        </main>
      </div>
    );
  }
  return (
    <div className="app-shell">
      <AppHeader />
      <main className="scenario-route">
        <p className="eyebrow">NEUROFLY / SCIENTIFIC SCENARIOS</p>
        <div className="library-heading">
          <div>
            <h1>Explore canonical scenarios.</h1>
            <p className="scenario-intro">
              Bounded connectome-based models. Explicit inputs. Frozen scientific results.
              Deterministic replay; browsing starts no simulation.
            </p>
          </div>
          <span className="library-count">
            {String(scenarios.length).padStart(2, "0")} <small>CANONICAL SCENARIOS</small>
          </span>
        </div>
        <section aria-label="Canonical scenario catalogue">
          <ScenarioCards scenarios={scenarios} />
        </section>
        <p className="subtle-note">
          These presets are separate from completed Phase 3B experiments, available
          through Experiments when compatible persisted artifacts are configured.
          Broader interactive simulation remains future work.
        </p>
      </main>
    </div>
  );
}
