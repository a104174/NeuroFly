export type LabTool = "explore" | "research" | "fly";

/**
 * What each Lab tool may say about itself. Every claim below is tied to a test or a report in the
 * repository (see docs/science-copy-review.md). A claim with no proof for a tool is not made for it.
 */
export const LAB_CLAIMS: Record<LabTool, { line: string; proof: ReadonlyArray<string>; paths: ReadonlyArray<string> }> = {
  explore: {
    line: "Kinematic model. No muscle or wing physics. Output is model state. The walking model runs in your browser. Live sessions are not saved or exported.",
    proof: [
      "The neural update is a TypeScript reimplementation of the pinned Python model. For the first 1,500 steps (30 seconds) a live session equals the finite navigation model step for step, and that model agrees with five recorded Python runs within 1e-8 in every model-space quantity (largest difference 4.97e-13).",
      "A session that runs longer continues with the same code, but there is no Python run to compare it with.",
      "Forward propulsion, boundary response and flight are engineering rules, not biology. Flight modes are not covered by the comparison above.",
    ],
    paths: [
      "web/tests/live-ground.test.ts (live prefix equals the finite model)",
      "web/tests/continuous-navigation.test.ts (parity within 1e-8 against the Python reference)",
      "docs/science/continuous_arena_navigation_v3.md (1,501 boundaries of five Python cases)",
      "docs/science/interactive_neural_locomotion_v2.md (401 boundaries, tolerance 1e-8)",
    ],
  },
  research: {
    line: "Kinematic model. No muscle or wing physics. Output is model state. Some modes run the model in your browser; others play back recorded Python runs and compute nothing.",
    proof: [
      "Modes that run in the browser use the same neural update as Explore, which agrees with the recorded Python runs within 1e-8 (see Explore). Replay modes show results that were computed in Python and fetched from the server.",
      "Runs you save in My Experiments are kept in this browser (IndexedDB), under this site's address. Clearing site data removes them. They are not sent to a server.",
    ],
    paths: [
      "web/tests/continuous-navigation.test.ts and docs/science/continuous_arena_navigation_v3.md (browser model against Python)",
      "web/tests/experiment-library.test.ts (saving, loading and deleting in IndexedDB)",
      "web/tests/read-only.test.ts (no source file sends a write request)",
    ],
  },
  fly: {
    line: "A visual model of the fly body. It shows no simulation and no neural activity. Output is a presentation.",
    proof: [
      "This viewer draws a 3D body asset in your browser. It runs no neural model, so no comparison with Python applies to it, and it saves nothing.",
    ],
    paths: ["web/src/app/visual-lab/fly/page.tsx (page description: no scientific simulation)"],
  },
};

