import type {
  MorphologyBody,
  MorphologyComponent,
  MorphologyNode,
} from "./neuroflyClient";

export const DNP01_MORPHOLOGY_VIEW_ID = "dnp01_morphology_view_v1" as const;
export const MORPHOLOGY_VIEW_TARGET_EXTENT = 8;

export interface MorphologyViewTransform {
  readonly view_id: typeof DNP01_MORPHOLOGY_VIEW_ID;
  readonly source_frame: "male_cns_v1_em_native_voxels";
  readonly source_unit: "8_nm_voxel";
  readonly source_bounds: {
    readonly minimum: readonly [number, number, number];
    readonly maximum: readonly [number, number, number];
  };
  readonly center_source: readonly [number, number, number];
  readonly uniform_scale: number;
  readonly axis_mapping: Readonly<{
    source_x: "view_x";
    source_y: "view_y";
    source_z: "view_z";
  }>;
}

export interface MorphologyLineComponent {
  readonly bodyId: 10001 | 10010;
  readonly componentId: number;
  readonly positions: Float32Array;
}

function allNodes(bodies: readonly MorphologyBody[]): MorphologyNode[] {
  return bodies.flatMap((body) =>
    body.components.flatMap((component) => component.nodes),
  );
}

export function deriveSharedMorphologyViewTransform(
  bodies: readonly MorphologyBody[],
): MorphologyViewTransform {
  if (bodies.length !== 2 || new Set(bodies.map((body) => body.body_id)).size !== 2) {
    throw new Error("The shared DNp01 view requires both distinct bodies.");
  }
  const nodes = allNodes(bodies);
  if (nodes.length === 0) throw new Error("Morphology view requires source nodes.");
  const minimum: [number, number, number] = [Infinity, Infinity, Infinity];
  const maximum: [number, number, number] = [-Infinity, -Infinity, -Infinity];
  for (const node of nodes) {
    const values = [node.x, node.y, node.z] as const;
    for (let axis = 0; axis < 3; axis += 1) {
      minimum[axis] = Math.min(minimum[axis], values[axis]);
      maximum[axis] = Math.max(maximum[axis], values[axis]);
    }
  }
  const center: [number, number, number] = [
    (minimum[0] + maximum[0]) / 2,
    (minimum[1] + maximum[1]) / 2,
    (minimum[2] + maximum[2]) / 2,
  ];
  const extent = Math.max(
    maximum[0] - minimum[0],
    maximum[1] - minimum[1],
    maximum[2] - minimum[2],
  );
  if (!(extent > 0) || !Number.isFinite(extent)) {
    throw new Error("Morphology source bounds must have finite non-zero extent.");
  }
  return Object.freeze({
    view_id: DNP01_MORPHOLOGY_VIEW_ID,
    source_frame: "male_cns_v1_em_native_voxels",
    source_unit: "8_nm_voxel",
    source_bounds: Object.freeze({
      minimum: Object.freeze(minimum),
      maximum: Object.freeze(maximum),
    }),
    center_source: Object.freeze(center),
    uniform_scale: MORPHOLOGY_VIEW_TARGET_EXTENT / extent,
    axis_mapping: Object.freeze({
      source_x: "view_x",
      source_y: "view_y",
      source_z: "view_z",
    }),
  });
}

export function transformMorphologyPoint(
  point: Pick<MorphologyNode, "x" | "y" | "z">,
  transform: MorphologyViewTransform,
): [number, number, number] {
  return [
    (point.x - transform.center_source[0]) * transform.uniform_scale,
    (point.y - transform.center_source[1]) * transform.uniform_scale,
    (point.z - transform.center_source[2]) * transform.uniform_scale,
  ];
}

function componentPositions(
  component: MorphologyComponent,
  transform: MorphologyViewTransform,
): Float32Array {
  const nodes = new Map(component.nodes.map((node) => [node.node_id, node]));
  const values: number[] = [];
  for (const link of component.links) {
    const child = nodes.get(link.child_node_id);
    const parent = nodes.get(link.parent_node_id);
    if (!child || !parent) throw new Error("Morphology link endpoint is unavailable.");
    values.push(
      ...transformMorphologyPoint(child, transform),
      ...transformMorphologyPoint(parent, transform),
    );
  }
  return new Float32Array(values);
}

export function buildMorphologyLineComponents(
  body: MorphologyBody,
  transform: MorphologyViewTransform,
): MorphologyLineComponent[] {
  return body.components.map((component) => ({
    bodyId: body.body_id,
    componentId: component.component_id,
    positions: componentPositions(component, transform),
  }));
}
