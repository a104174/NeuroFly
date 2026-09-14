import Link from "next/link";

import { AppHeader } from "@/components/AppHeader";
import { StateMessage } from "@/components/StateMessage";
import {
  listMorphologyArtifacts,
  NeuroflyApiError,
  type MorphologyArtifactSummary,
} from "@/lib/neuroflyClient";

export const dynamic = "force-dynamic";

export default async function MorphologyPage() {
  let artifacts: MorphologyArtifactSummary[] | null = null;
  let requestError: unknown = null;
  try {
    artifacts = await listMorphologyArtifacts();
  } catch (error) {
    requestError = error;
  }
  return (
    <div className="app-shell">
      <AppHeader />
      <main className="main-content main-content-wide">
        {requestError ? (
          <StateMessage
            eyebrow="MORPHOLOGY API UNAVAILABLE"
            title="The raw morphology catalogue could not load."
            detail={
              requestError instanceof NeuroflyApiError
                ? requestError.message
                : "The morphology API could not be reached."
            }
            tone="error"
          />
        ) : !artifacts || artifacts.length === 0 ? (
          <StateMessage
            eyebrow="NO RAW MORPHOLOGY"
            title="No morphology artifacts are available."
            detail="Generate and configure a validated MaleCNS morphology artifact. The browser never fetches neuPrint directly."
          />
        ) : (
          <section className="morphology-catalogue">
            <p className="eyebrow">MALECNS / READ-ONLY INSPECTION</p>
            <h1>Raw bounded morphology samples</h1>
            <p>
              Source-coordinate skeleton artifacts are separate from experiment
              playback and the presentation-only fly scene.
            </p>
            <ul>
              {artifacts.map((artifact) => (
                <li key={artifact.artifact_id}>
                  <Link href={`/morphology/${artifact.artifact_id}`}>
                    <strong>
                      {artifact.bodies.map((body) => body.neuron_type).filter(
                        (value, index, values) => values.indexOf(value) === index,
                      ).join(" + ")} · {artifact.body_ids.length} bodies
                    </strong>
                    <span>{artifact.dataset}</span>
                    <span>{artifact.coordinate_frame_id}</span>
                    <span>{artifact.artifact_id.slice(0, 16)}…</span>
                  </Link>
                </li>
              ))}
            </ul>
          </section>
        )}
      </main>
    </div>
  );
}
