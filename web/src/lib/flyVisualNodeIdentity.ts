import type { Object3D } from "three";
import type { GLTFParser } from "three/examples/jsm/loaders/GLTFLoader.js";

export type VisualNodeParser = Pick<GLTFParser, "json" | "associations">;

/** Source node indices are authoritative. Never guess by stripping punctuation or extras. */
export function visualNodeIdentity(source: Object3D, parser?: VisualNodeParser): Map<string, Object3D> {
  if (parser && !Array.isArray(parser.json?.nodes)) throw new Error("Missing glTF source node definitions.");
  const identities = new Map<string, Object3D>();
  const indices = new Set<number>();
  source.traverse(node => {
    let name = node.name;
    if (parser) {
      const index = parser.associations.get(node)?.nodes;
      if (index === undefined) return;
      if (!Number.isInteger(index) || index < 0 || !Array.isArray(parser.json.nodes) || index >= parser.json.nodes.length || indices.has(index)) {
        throw new Error("Invalid or ambiguous glTF source node index.");
      }
      indices.add(index);
      const definition = parser.json.nodes[index];
      if (!definition || (definition.name !== undefined && typeof definition.name !== "string")) throw new Error("Invalid glTF source node name.");
      name = definition.name ?? "";
    }
    if (!name) return;
    if (identities.has(name)) throw new Error("Duplicate or ambiguous anatomical source identity.");
    identities.set(name, node);
  });
  if (parser && indices.size === 0) throw new Error("No glTF source associations for this scene; use the verified clone identity map.");
  return identities;
}

/** Object3D.clone(true) retains ordered topology, not parser associations. */
export function cloneVisualNodeIdentity(source: Object3D, clone: Object3D, verified: ReadonlyMap<string, Object3D>): Map<string, Object3D> {
  const counterparts = new Map<Object3D, Object3D>();
  function pair(original: Object3D, instance: Object3D) {
    if (original === instance || original.type !== instance.type || original.name !== instance.name || original.children.length !== instance.children.length) {
      throw new Error("Visual clone hierarchy does not match the verified source.");
    }
    counterparts.set(original, instance);
    original.children.forEach((child, i) => pair(child, instance.children[i]));
  }
  pair(source, clone);
  const identities = new Map<string, Object3D>();
  const claimed = new Set<Object3D>();
  for (const [name, original] of verified) {
    const instance = counterparts.get(original);
    if (!instance || claimed.has(instance)) throw new Error("Missing or ambiguous cloned source identity.");
    claimed.add(instance); identities.set(name, instance);
  }
  return identities;
}
