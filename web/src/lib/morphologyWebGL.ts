export type MorphologyWebGLCapability = "pending" | "available" | "unavailable";

export type MorphologyWebGLView = "placeholder" | "canvas" | "fallback";

export const INITIAL_MORPHOLOGY_WEBGL_CAPABILITY: MorphologyWebGLCapability = "pending";

export function subscribeToMorphologyWebGLCapability(): () => void {
  return () => {};
}

let clientCapability: Exclude<MorphologyWebGLCapability, "pending"> | undefined;

export function getMorphologyWebGLCapability(): MorphologyWebGLCapability {
  if (clientCapability !== undefined) return clientCapability;
  try {
    const canvas = document.createElement("canvas");
    const context = canvas.getContext("webgl2") ?? canvas.getContext("webgl");
    clientCapability = context ? "available" : "unavailable";
  } catch {
    clientCapability = "unavailable";
  }
  return clientCapability;
}

export function getServerMorphologyWebGLCapability(): MorphologyWebGLCapability {
  return INITIAL_MORPHOLOGY_WEBGL_CAPABILITY;
}

export function selectMorphologyWebGLView(
  capability: MorphologyWebGLCapability,
): MorphologyWebGLView {
  switch (capability) {
    case "pending":
      return "placeholder";
    case "available":
      return "canvas";
    case "unavailable":
      return "fallback";
  }
}
