import Link from "next/link";
import { Arrow, ActionLink } from "../site/SitePrimitives";
import { LabPreview } from "../site/LabPreview";
import { experimentMetadata } from "@/lib/scenarioPresentation";
import type { ScenarioDefinition, ScenarioKind } from "@/lib/scenarioPlayback";

/** Friendly labels over the five existing IDs. Never used to construct model inputs. */
export const discoveryCopy: Record<ScenarioKind, { title: string; description: string; category: string }> = {
  BASELINE_CONTROL: { title: "Begin with stillness", description: "A quiet reference. See what the selected model does when no effective stimulus is present.", category: "Control" },
  LOOMING_CIRCUIT_VALIDATION: { title: "An approaching object", description: "Follow a brief visual input through a selected circuit. A neural response can occur while the body stays still.", category: "Visual circuit" },
  LOOMING_WORLD_EXPERIMENT: { title: "A changing field of view", description: "Inspect a longer, prescribed approach and the recorded neural and body outputs it produces.", category: "World & perception" },
  HORIZONTAL_MOTION_NEURAL_VALIDATION: { title: "Motion into neural activity", description: "Trace a horizontal-motion descriptor through HS and DNp15 model states. This experiment has no body movement mapping.", category: "Neural dynamics" },
  EXPLORATORY_COURSE_CONTROL: { title: "A turn through feedback", description: "Explore how visual-motion feedback changes model orientation after a perturbation. Orientation only; no translation.", category: "Closed-loop model" },
};

/** Conceptual marks, not telemetry, measured graphs or screenshots. */
function ScenarioMark({ id }: { id: ScenarioKind }) {
  const motion = id === "HORIZONTAL_MOTION_NEURAL_VALIDATION", feedback = id === "EXPLORATORY_COURSE_CONTROL";
  return <svg className="discovery-mark" viewBox="0 0 320 150" fill="none" aria-hidden="true">
    <path className="mark-guide" d="M25 75h270M160 15v120" />
    {id === "BASELINE_CONTROL" ? <><circle cx="160" cy="75" r="35" /><circle cx="160" cy="75" r="5" fill="currentColor" /><path d="M100 75h-20m140 0h20" /></> : feedback ? <><path d="M123 40a45 45 0 1 1-5 65M110 30l13 10-14 9" /><path d="m145 82 24-14-6 26" /><circle cx="160" cy="75" r="64" className="mark-guide" /></> : motion ? <><path d="M45 55h50m-13-9 13 9-13 9m-37 31h50m-13-9 13 9-13 9M130 75l48-27m-48 27 48 27m12-54 60 27-60 27" />{[[125,75],[184,48],[184,102],[257,75]].map(([x,y])=><circle key={`${x}:${y}`} cx={x} cy={y} r="7" fill="var(--nf-bg)" />)}</> : <><circle cx="96" cy="75" r="12" /><path d="m124 75 65 0m-12-9 12 9-12 9" /><path d="M215 50a30 30 0 0 1 0 50m12-65a48 48 0 0 1 0 80" />{id === "LOOMING_WORLD_EXPERIMENT" ? <path d="M241 21a65 65 0 0 1 0 108" /> : null}</>}
  </svg>;
}

export function ScenarioDiscovery({ scenarios }: { scenarios: ScenarioDefinition[] }) {
  return <>
    <section className="discovery-lab" aria-labelledby="live-lab-title">
      <div className="discovery-lab-copy"><p className="nf-eyebrow"><span className="nf-small-dot" aria-hidden="true" /> Interactive laboratory</p><h2 id="live-lab-title">Start with a little <br />exploration.</h2><p>Watch the digital fly move through its enclosure. Pause, change your view and look closer at model neural influence.</p><ActionLink href="/visual-lab/arena">Enter the Lab</ActionLink><small>Live browser model · Engineering movement</small></div>
      <LabPreview />
    </section>
    <section className="discovery-catalogue" aria-labelledby="catalogue-title">
      <div className="discovery-section-heading"><div><p className="nf-eyebrow">A question at a time</p><h2 id="catalogue-title">Look beneath the behaviour.</h2></div><p>Five controlled experiments.<br />Recorded results, ready to inspect.</p></div>
      <div className="discovery-grid">{scenarios.map((scenario, index) => {
        const copy = discoveryCopy[scenario.id], meta = experimentMetadata[scenario.id];
        return <article className={`discovery-card discovery-card--${index}`} key={scenario.id} data-scenario-id={scenario.id}>
          <div className="discovery-card-visual"><span>{String(index + 1).padStart(2, "0")} / {copy.category}</span><ScenarioMark id={scenario.id} /><small>Concept diagram · not measured data</small></div>
          <div className="discovery-card-body"><p className="discovery-format">Canonical replay <span>{meta.duration}</span></p><h3>{copy.title}</h3><p>{copy.description}</p><Link prefetch={false} className="discovery-text-link" href={`/scenarios/${scenario.id}`} aria-label={`Open ${scenario.title}`}>View experiment <Arrow /></Link>
            <details className="discovery-context"><summary>Model context</summary><dl><div><dt>Source preset</dt><dd>{scenario.title}</dd></div><div><dt>Type</dt><dd>{meta.kind}</dd></div><div><dt>Output</dt><dd>{meta.scope}</dd></div><div><dt>Limit</dt><dd>{meta.limit}</dd></div></dl><p>{scenario.scientific_caveat}</p></details>
          </div>
        </article>;
      })}</div>
      <p className="discovery-caption">These are bounded computational experiments. Selected biological connections inform the models; sensory encoding, dynamics and motor mappings include explicit assumptions.</p>
    </section>
    <section className="discovery-research"><div><p className="nf-eyebrow">For a closer inspection</p><h2>Keep asking questions.</h2><p>Five executable presets form this catalogue. Historical modes, diagnostics and session tools remain in the research archive.</p></div><Link prefetch={false} className="discovery-text-link" href="/visual-lab/arena/research">Open research tools <Arrow /></Link></section>
  </>;
}
