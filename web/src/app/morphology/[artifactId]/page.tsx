import Link from "next/link";
import { notFound } from "next/navigation";

import { AppHeader } from "@/components/AppHeader";
import { MorphologyInspector } from "@/components/MorphologyInspector";
import {
  getMorphologyArtifact,
  getMorphologyBody,
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
      }
    | null = null;
  let requestError: unknown = null;
  try {
    const artifact = await getMorphologyArtifact(artifactId);
    const bodies = await Promise.all(
      artifact.body_ids.map((bodyId) => getMorphologyBody(artifactId, bodyId)),
    );
    data = { artifact, bodies };
  } catch (error) {
    requestError = error;
  }
  if (requestError instanceof NeuroflyApiError && requestError.status === 404) {
    notFound();
  }
  if (requestError || !data) {
    throw requestError instanceof Error
      ? requestError
      : new Error("Morphology API returned an invalid response.");
  }
  return (
      <div className="app-shell">
        <AppHeader />
        <main className="main-content main-content-wide">
          <Link className="back-link" href="/morphology">
            ← Morphology catalogue
          </Link>
          <MorphologyInspector
            artifact={data.artifact}
            bodies={data.bodies}
          />
        </main>
      </div>
  );
}
