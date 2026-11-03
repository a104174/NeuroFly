"use client";

import { useSyncExternalStore, type ReactNode } from "react";
import { StatePanel } from "@/components/ui/StatePanel";
import { getMorphologyWebGLCapability, getServerMorphologyWebGLCapability, subscribeToMorphologyWebGLCapability } from "@/lib/morphologyWebGL";

/** Shows a useful message instead of a blank stage when the browser has no WebGL. */
export function WebGLGate({ children, hasDataAlternative = true }: { children: ReactNode; hasDataAlternative?: boolean }) {
  const capability = useSyncExternalStore(subscribeToMorphologyWebGLCapability, getMorphologyWebGLCapability, getServerMorphologyWebGLCapability);
  if (capability === "unavailable") return <StatePanel state="webgl-off" hasDataAlternative={hasDataAlternative} headingLevel={3} />;
  return <>{children}</>;
}
