// Routes and fixture IDs shared by the checks. The IDs are the recorded artifacts of the local dataset.
export const EXP = "63a73b7ea3ba10a5850b166598f134a2dc0a752bf93c550e2371ee8d5b1bf656";
export const MOR_DNP = "719426f0cd2db586b149943483abfe6519d45c4a39fb48aa1f4a566c514c84f3";
export const MOR_SIX = "a3f090d5309d9ede0e9e0f78343a618a4bafba3fea91e5a27d37927d5ec55f79";
export const ROUTES = [
  ["home", "/", 200], ["scenarios", "/scenarios", 200], ["scenario-looming", "/scenarios/LOOMING_CIRCUIT_VALIDATION", 200],
  ["scenario-replay", "/scenarios/LOOMING_CIRCUIT_VALIDATION?replay=canonical", 200], ["scenario-course", "/scenarios/EXPLORATORY_COURSE_CONTROL", 200],
  ["experiments", "/experiments", 200], ["experiment", `/experiments/${EXP}`, 200], ["cockpit", `/experiments/${EXP}/cockpit`, 200],
  ["neurons", "/morphology", 200], ["neurons-dnp01", `/morphology/${MOR_DNP}`, 200], ["neurons-six", `/morphology/${MOR_SIX}`, 200],
  ["lab", "/visual-lab", 200], ["lab-arena", "/visual-lab/arena", 200], ["lab-research", "/visual-lab/arena/research", 200], ["lab-fly", "/visual-lab/fly", 200],
  ["science", "/science", 200], ["science-status", "/science/status", 200], ["science-glossary", "/science/glossary", 200],
  ["404", "/does-not-exist", 404], ["404-experiment", "/experiments/abc123", 404], ["404-scenario", "/scenarios/NOPE", 404], ["404-neurons", `/morphology/${"0".repeat(64)}`, 404],
];
/** Pages that must not load three.js (brief section 11, Bundle). */
export const NO_3D = ["home", "scenarios", "experiments", "science", "science-status", "science-glossary", "neurons", "lab"];
export const WIDTHS = [360, 390, 768, 1024, 1440, 1920];
