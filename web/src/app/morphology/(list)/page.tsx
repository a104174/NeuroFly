import type { Metadata } from "next";
import { PageShell } from "@/components/site/PageShell";
import { ButtonLink, Card, KindBadge, StatePanel } from "@/components/ui";
import { listMorphologyArtifacts, NeuroflyApiError, type MorphologyArtifactSummary } from "@/lib/neuroflyClient";
import styles from "./page.module.css";

export const dynamic = "force-dynamic";
export const metadata: Metadata = {
  title: "Neurons · NeuroFly",
  description: "Reconstructed shapes of real fruit fly neurons from the MaleCNS connectome. Read-only.",
};

function label(artifact: MorphologyArtifactSummary): string {
  const types = artifact.bodies.map((body) => body.neuron_type).filter((value, index, values) => values.indexOf(value) === index);
  return types.join(" + ");
}

export default async function MorphologyPage() {
  let artifacts: MorphologyArtifactSummary[] | null = null;
  let failure: string | null = null;
  try { artifacts = await listMorphologyArtifacts(); }
  catch (error) { failure = error instanceof NeuroflyApiError ? error.message : "The morphology API could not be reached."; }
  return (
    <PageShell
      eyebrow="Structural"
      title="Neurons"
      current="/morphology"
      lead={<p>This is the reconstructed shape of real neurons, not a simulation. Each sample is a set of source skeletons from the MaleCNS connectome.</p>}
    >
      {failure ? (
        <>
          <StatePanel state="api-down" actions={<ButtonLink href="/morphology">Retry</ButtonLink>} />
          <details className={styles.technical}><summary>Technical details</summary><p>{failure}</p></details>
        </>
      ) : !artifacts || artifacts.length === 0 ? (
        <StatePanel state="missing-data" what="Neuron shapes" detail="No morphology artifact is available. The browser never fetches neuPrint directly." />
      ) : (
        <ul className={styles.grid}>
          {artifacts.map((artifact) => (
            <li key={artifact.artifact_id}>
              <Card
                eyebrow="Neuron shapes"
                title={`${label(artifact)} · ${artifact.body_ids.length} ${artifact.body_ids.length === 1 ? "body" : "bodies"}`}
                href={`/morphology/${artifact.artifact_id}`}
                variant="interactive"
                meta={[{ label: "Kind", value: <KindBadge kind="structural" /> }]}
              >
                <p>{artifact.dataset}. Coordinate frame {artifact.coordinate_frame_id}.</p>
                <p className={styles.id}>{artifact.artifact_id}</p>
              </Card>
            </li>
          ))}
        </ul>
      )}
    </PageShell>
  );
}
