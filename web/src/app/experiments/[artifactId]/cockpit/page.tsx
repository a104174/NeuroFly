import Link from "next/link";
import { notFound } from "next/navigation";

import { AppHeader } from "@/components/AppHeader";
import { ScientificCockpit } from "@/components/ScientificCockpit";
import { StateMessage } from "@/components/StateMessage";
import {
  COCKPIT_MORPHOLOGY_ARTIFACT_ID,
  validateCockpitConnectivity,
  validateCockpitExperiment,
  validateCockpitMorphology,
} from "@/lib/cockpitModel";
import {
  getExperiment,
  getMorphologyArtifact,
  getMorphologyBody,
  getStructuralConnectivity,
  getTimeline,
  NeuroflyApiError,
  type ExperimentSummary,
  type ExperimentTimeline,
  type MorphologyArtifactSummary,
  type MorphologyBody,
  type StructuralConnectivityProjection,
} from "@/lib/neuroflyClient";

export const dynamic = "force-dynamic";

function readableFailure(error: unknown): string {
  return error instanceof NeuroflyApiError || error instanceof Error
    ? error.message
    : "The read-only source could not be validated.";
}

export default async function ScientificCockpitPage({
  params,
}: {
  params: Promise<{ artifactId: string }>;
}) {
  const { artifactId } = await params;
  let core: { summary: ExperimentSummary; timeline: ExperimentTimeline } | null = null;
  let coreError: unknown = null;
  try {
    const [summary, timeline] = await Promise.all([
      getExperiment(artifactId),
      getTimeline(artifactId),
    ]);
    validateCockpitExperiment(summary, timeline);
    core = { summary, timeline };
  } catch (error) {
    coreError = error;
  }
  if (coreError instanceof NeuroflyApiError && coreError.code === "artifact_not_found") {
    notFound();
  }
  if (!core) {
    return <div className="app-shell cockpit-shell">
      <AppHeader />
      <main className="cockpit-route cockpit-route-error">
        <Link className="back-link" href="/">← all experiments</Link>
        <StateMessage eyebrow="EXPERIMENT UNAVAILABLE" title="This run cannot open in the Scientific Cockpit." detail={readableFailure(coreError)} tone="error" />
      </main>
    </div>;
  }

  const [morphologyResult, connectivityResult] = await Promise.allSettled([
    getMorphologyArtifact(COCKPIT_MORPHOLOGY_ARTIFACT_ID),
    getStructuralConnectivity(),
  ]);
  let morphology: MorphologyArtifactSummary | null = null;
  let bodies: MorphologyBody[] = [];
  let morphologyFailure: string | null = null;
  if (morphologyResult.status === "fulfilled") {
    try {
      const loaded = morphologyResult.value;
      const loadedBodies = await Promise.all(loaded.body_ids.map((bodyId) =>
        getMorphologyBody(loaded.artifact_id, bodyId),
      ));
      validateCockpitMorphology(core.summary, loaded, loadedBodies);
      morphology = loaded;
      bodies = loadedBodies;
    } catch (error) {
      morphologyFailure = readableFailure(error);
    }
  } else {
    morphologyFailure = readableFailure(morphologyResult.reason);
  }

  let connectivity: StructuralConnectivityProjection | null = null;
  let connectivityFailure: string | null = null;
  if (connectivityResult.status === "fulfilled" && morphology) {
    try {
      validateCockpitConnectivity(core.summary, morphology, connectivityResult.value);
      connectivity = connectivityResult.value;
    } catch (error) {
      connectivityFailure = readableFailure(error);
    }
  } else if (connectivityResult.status === "rejected") {
    connectivityFailure = readableFailure(connectivityResult.reason);
  }

  return (
    <div className="app-shell cockpit-shell">
      <AppHeader />
      <main className="cockpit-route">
        <div className="cockpit-route-nav">
          <Link href="/">← all experiments</Link>
          <Link href={`/experiments/${artifactId}`}>Standalone playback ↗</Link>
        </div>
        <ScientificCockpit
          summary={core.summary}
          timeline={core.timeline}
          morphology={morphology}
          bodies={bodies}
          connectivity={connectivity}
          morphologyFailure={morphologyFailure}
          connectivityFailure={connectivityFailure}
        />
      </main>
    </div>
  );
}
