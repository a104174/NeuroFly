import type {
  MorphologyBody,
  StructuralConnectivityProjection,
} from "./neuroflyClient";
import {
  bodySourceBounds,
  transformMorphologyPoint,
  type MorphologySelection,
  type MorphologyViewTransform,
} from "./morphologyView";

export interface SchematicStructuralConnector {
  readonly preBodyId: number;
  readonly postBodyId: number;
  readonly start: readonly [number, number, number];
  readonly end: readonly [number, number, number];
  readonly highlighted: boolean;
  readonly opacity: number;
  readonly visible: boolean;
}

export function deriveStructuralBodyAnchors(
  bodies: readonly MorphologyBody[],
  transform: MorphologyViewTransform,
): ReadonlyMap<number, readonly [number, number, number]> {
  return new Map(bodies.map((body) => {
    const bounds = bodySourceBounds(body);
    const center = {
      x: (bounds.minimum[0] + bounds.maximum[0]) / 2,
      y: (bounds.minimum[1] + bounds.maximum[1]) / 2,
      z: (bounds.minimum[2] + bounds.maximum[2]) / 2,
    };
    return [body.body_id, transformMorphologyPoint(center, transform)] as const;
  }));
}

export function buildSchematicStructuralConnectors(
  projection: StructuralConnectivityProjection,
  bodies: readonly MorphologyBody[],
  transform: MorphologyViewTransform,
  selection: MorphologySelection,
  visibility: Readonly<Record<MorphologyBody["body_id"], boolean>>,
): SchematicStructuralConnector[] {
  const anchors = deriveStructuralBodyAnchors(bodies, transform);
  return projection.edges.map((edge) => {
    const start = anchors.get(edge.pre_body_id);
    const end = anchors.get(edge.post_body_id);
    if (!start || !end) throw new Error("Connectivity endpoint is outside the loaded morphology sample.");
    const highlighted = selection.bodyId === null ||
      selection.bodyId === edge.pre_body_id || selection.bodyId === edge.post_body_id;
    return {
      preBodyId: edge.pre_body_id,
      postBodyId: edge.post_body_id,
      start,
      end,
      highlighted,
      opacity: highlighted ? 0.82 : 0.14,
      visible: visibility[edge.pre_body_id] && visibility[edge.post_body_id],
    };
  });
}
