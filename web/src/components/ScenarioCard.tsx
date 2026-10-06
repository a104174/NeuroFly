import Link from "next/link";
import { experimentMetadata } from "@/lib/scenarioPresentation";
import type { ScenarioDefinition } from "@/lib/scenarioPlayback";

export function ScenarioCard({scenario,index}:{scenario:ScenarioDefinition;index:number}) {
  const meta=experimentMetadata[scenario.id];
  return <Link href={`/scenarios/${scenario.id}`} className="scenario-card" aria-label={`Open ${scenario.title}`}>
    <span className="experiment-number" aria-hidden="true">{String(index+1).padStart(2,"0")}</span>
    <div className="card-identity"><span className="eyebrow">{meta.kind}</span><h2>{scenario.title}</h2><p>{meta.purpose}</p><small>{meta.limit}</small></div>
    <dl className="card-metadata"><div><dt>Scientific horizon</dt><dd>{meta.duration}</dd></div><div><dt>Input</dt><dd>{meta.input}</dd></div><div><dt>Output scope</dt><dd>{meta.scope}</dd></div><div><dt>Canonical outcome</dt><dd>{meta.outcome}</dd></div></dl>
    <span className="card-open"><span>Canonical replay available</span><b aria-hidden="true">↗</b></span>
  </Link>;
}
