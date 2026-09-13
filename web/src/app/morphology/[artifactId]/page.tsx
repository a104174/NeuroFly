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
        body10001: Awaited<ReturnType<typeof getMorphologyBody>>;
        body10010: Awaited<ReturnType<typeof getMorphologyBody>>;
      }
    | null = null;
  let requestError: unknown = null;
  try {
    const [artifact, body10001, body10010] = await Promise.all([
      getMorphologyArtifact(artifactId),
      getMorphologyBody(artifactId, 10001),
      getMorphologyBody(artifactId, 10010),
    ]);
    data = { artifact, body10001, body10010 };
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
            bodies={[data.body10001, data.body10010]}
          />
        </main>
      </div>
  );
}
