import Link from "next/link";
import { notFound } from "next/navigation";

import { PageShell } from "@/components/site/PageShell";
import { ButtonLink, StatePanel } from "@/components/ui";
import styles from "../(list)/page.module.css";
import { MorphologyInspector } from "@/components/MorphologyInspector";
import {
  getMorphologyArtifact,
  getMorphologyBody,
  getStructuralConnectivity,
  NeuroflyApiError,
} from "@/lib/neuroflyClient";

export const dynamic = "force-dynamic";

export default async function MorphologyArtifactPage({
  params,
}: {
  params: Promise<{ artifactId: string }>;
}) {
  const { artifactId } = await params;
  let data:
    | {
        artifact: Awaited<ReturnType<typeof getMorphologyArtifact>>;
        bodies: Awaited<ReturnType<typeof getMorphologyBody>>[];
        connectivity: Awaited<ReturnType<typeof getStructuralConnectivity>>;
      }
    | null = null;
  let requestError: unknown = null;
  try {
    const artifact = await getMorphologyArtifact(artifactId);
    const [bodies, connectivity] = await Promise.all([
      Promise.all(artifact.body_ids.map((bodyId) => getMorphologyBody(artifactId, bodyId))),
      getStructuralConnectivity(),
    ]);
    data = { artifact, bodies, connectivity };
  } catch (error) {
    requestError = error;
  }
  if (requestError instanceof NeuroflyApiError && requestError.status === 404) {
    notFound();
  }
  if (requestError || !data) {
    const integrity = requestError instanceof NeuroflyApiError && (requestError.status === 409 || requestError.code === "artifact_integrity_failure");
    return (
      <PageShell title="These neuron shapes could not be read" current="/morphology">
        <StatePanel state={integrity ? "integrity-failure" : "api-down"} actions={<ButtonLink href="/morphology">Back to Neurons</ButtonLink>} />
      </PageShell>
    );
  }
  const names = data.artifact.bodies.map((body) => body.neuron_type).filter((value, index, values) => values.indexOf(value) === index).join(" + ");
  return (
    <PageShell
      eyebrow="Neurons"
      title={`${names} · ${data.artifact.body_ids.length} ${data.artifact.body_ids.length === 1 ? "body" : "bodies"}`}
      current="/morphology"
      lead={<p>This is the reconstructed shape of real neurons, not a simulation.</p>}
    >
      <Link className={styles.back} href="/morphology" prefetch={false}>← Neurons</Link>
      <MorphologyInspector artifact={data.artifact} bodies={data.bodies} connectivity={data.connectivity} />
    </PageShell>
  );
}
