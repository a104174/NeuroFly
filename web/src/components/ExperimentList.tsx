import Link from "next/link";

import type { ExperimentSummary } from "@/lib/neuroflyClient";

function shortId(value: string) {
  return `${value.slice(0, 12)}…`;
}

function formatMs(value: number) {
  return `${value.toFixed(value % 1 === 0 ? 0 : 2)} ms`;
}

export function ExperimentList({ experiments }: { experiments: ExperimentSummary[] }) {
  return (
    <nav className="experiment-list" aria-label="Completed experiments">
      <div className="list-heading">
        <div>
          <p className="eyebrow">RUN CATALOGUE</p>
          <h2>Completed experiments</h2>
        </div>
        <span className="count-badge">{experiments.length.toString().padStart(2, "0")}</span>
      </div>
      <ul>
        {experiments.map((experiment) => (
          <li key={experiment.artifact_id}>
            <Link className="experiment-link" href={`/experiments/${experiment.artifact_id}`}>
              <span className="experiment-link-topline">
                <strong>{experiment.candidate.identifier}</strong>
                <span className="pathway-chip">{experiment.pathway_condition}</span>
              </span>
              <span className="experiment-link-meta">
                <span title={experiment.artifact_id}>#{shortId(experiment.artifact_id)}</span>
                <span>{formatMs(experiment.duration_ms)}</span>
                <span>dt {formatMs(experiment.dt_ms)}</span>
              </span>
              <span className="experiment-link-status">
                <span className="status-dot status-dot-muted" aria-hidden="true" />
                {experiment.validation_status.replaceAll("_", " ")}
              </span>
            </Link>
          </li>
        ))}
      </ul>
    </nav>
  );
}
