# Phase 24 — second circuit evidence and selection gate

## Decision and scope

`SECOND_CIRCUIT_SELECTED_FOR_BOUNDED_VALIDATION`

Selected candidate: `hs_dnp15_horizontal_motion`. Capability class:
`VISUAL_COURSE_CONTROL`, narrowly a **neural foundation for horizontal-motion
course control**, not demonstrated steering or navigation. The first future
implementation is an eight-neuron, six-edge HS→DNp15 chemical feedforward
readout probe. No candidate was simulated in this phase.

Only this candidate meets `READY_FOR_BOUNDED_VALIDATION_DESIGN` under its
explicitly restricted boundary. Readiness is for exploratory neural validation,
not physiological calibration, complete network reconstruction or embodiment.
The circuit adds a directional visual-motion descending readout distinct from
the v1 looming/Giant Fiber axis. Its downstream biomechanics are excluded.

## Repository and frozen source

Initial worktree was clean; `main == origin/main` at
`a6ce8b412bf0cb84a3c46620e3b9c7d391f50ec7` (committed Phase 23).
The committed `neurofly_v1_scientific_status_v1` authority was independently
canonical-hashed as
`1aa1a39710ebc68030834b3a04ea202eb57fb25a0080f444db0ea19af64730a6`.
The v1 manifest and all implementation remain unchanged.

The full Phase 7O numerical replay, Phase 8C production replay, Phase 13B
closed-loop replay, corrected Phase 16 diagnostic replay and Phase 18 world
experiment replay passed before research/edits. Canonical IDs:

| Authority | Unchanged artifact ID |
| --- | --- |
| 7O | `99eeea47542abd5f9af2c1918e6e0514fa2c4b8f04d9a3f14a75ac1f8dbbcaa5` |
| 8C | `5f57cbc6c0ac770d65582ffe97c0c690e539bab33fef549da15d5273912279bf` |
| 13B | `55e2f4d37bc6f8fb81aee67886d8680a76646a0317961bd90cf0e3fbabb2c46b` |
| Corrected 16 | `bb1d227dd3dc56d74939c37e231ca0f8aa02f8d0140964eef7f1fb31e00b101b` |
| 18 | `ee781bd8c7e903c5fab78aff02d916fe68d26998a7caf774806778cacd2b616c` |

The v1 transfer coefficient, unnormalized sum, neural parameters, scenarios,
preregistration, motor path, body plant, API and frontend are not modified.
`ConnectsTo.weight` remains structural contact count, never efficacy.

## Selection method and public evidence

Scientific gates precede product considerations: structural presence (G1),
bounded definition (G2), primary functional evidence (G3), input semantics (G4),
output semantics (G5), manageable assumptions (G6), reproducible experiment
(G7), genuinely new capability (G8). No numeric score or visually desirable
outcome was used. The three serious candidates arise from primary experiments;
their nominated identities/routes were checked against the actual pinned dataset.

Authenticated read-only queries used `neuprint-python 0.6.3`,
`https://neuprint.janelia.org`, dataset `male-cns:v1.0`, on 2026-10-02.
The JSON preserves six exact Cypher queries, ordered bounded result records,
response hashes and query scope. `somaSide`, not morphology coordinates,
supplies laterality. Negative exact-name or direct-edge queries are not proof
that a biological population or indirect pathway is absent.
[Official MaleCNS source](https://www.janelia.org/project-team/flyem/male-cns-connectome).

The public primary sources were checked to the extent recorded in the JSON:

- [Erginkaya et al., 2025](https://www.nature.com/articles/s41593-025-01948-9):
  accessible original full text connects HS with DNp15/DNHS1, measures visual
  responses and reports walking-direction effects of unilateral silencing.
  The full mechanism includes a larger recurrent/disinhibitory network and
  electrical coupling; the selected motif cannot reproduce that mechanism.
  Physiological and behavioral preparations/sexes differ, and the paper's EM
  sources are not interchangeable with this live MaleCNS snapshot.
- [Suver et al., 2016](https://pmc.ncbi.nlm.nih.gov/articles/PMC5125229/):
  original indexed text/figure descriptions identify DNHS1 coupling with HS
  and whole-cell responses to rotational visual motion. Direct full-text access
  was restricted during this audit; the independently accessible 2025 primary
  paper supports the material selection claim. No fitted gain is imported.
- [Sen et al., 2017](https://pubmed.ncbi.nlm.nih.gov/28238656/): original
  abstract describes LC16-dependent recruitment of MDNs and backward/directional
  retreat using imaging and manipulations. This functional relationship does
  not establish a direct LC16→MDN edge or identify the missing MaleCNS relay.
- [Ache et al., 2019, landing study](https://pmc.ncbi.nlm.nih.gov/articles/PMC7444277/):
  original full-text XML was accessible through
  [Europe PMC](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC7444277/fullTextXML).
  DNp07/DNp10 recordings and manipulations support state-dependent landing-leg
  responses to visual expansion. LPLC3/LPLC4 terminal overlap motivates a
  candidate, but overlap is not itself structural connection evidence.

These studies concern Drosophila melanogaster. Naming compatibility is at
neuron-type level, not exact specimen/body-ID equivalence. Functional importance
does not identify per-edge magnitude, normalization or biological time constants.

The [Erginkaya public dataset](https://zenodo.org/records/14967806), DOI
`10.5281/zenodo.14967806`, has a CC BY 4.0 metadata record, a README and a
23,534,730,237-byte `data.zip`. Only metadata/README were inspected in memory;
the large archive was not downloaded. The README points to public associated
code, not executed or used as a source of NeuroFly parameters. Availability is
not an assay-calibration claim. Landing raw-data availability is request-based;
neither that nor author clarification is a dependency of the selected probe.

## Candidate comparison

| Candidate | New capability | MaleCNS support | Input/output readiness | Body compatibility | Assumption risk | Classification |
| --- | --- | --- | --- | --- | --- | --- |
| HS→DNp15 | Horizontal-motion descending readout | Six HS, two DNp15, six ipsilateral feedforward edges | New exploratory HS input; two neural readouts | Body output not required | Bounded encoder/dynamics; full network and yaw excluded | `READY_FOR_BOUNDED_VALIDATION_DESIGN` |
| LC16→MDN | Backward/directional retreat pathway | 182 LC16, four MDN; no direct edges returned; relay unverified | Expansion primitive potentially reusable after LC16 audit; upstream routing incomplete | Reverse proxy needs bounded extension; gait needs more | Unverified relay plus locomotor mapping | `STRUCTURAL_SUPPORT_INSUFFICIENT` |
| LPLC3/4→DNp07/DNp10 | Landing-related descending response | 97 LPLC4, four output DNs, 118 LPLC4 edges; exact LPLC3 label not returned | New dark-edge input feasible; state gating/boundary unresolved | Landing needs major biomechanics; later neural-only alternative possible | Missing identity/alias, flight state and effectors | `STRUCTURAL_SUPPORT_INSUFFICIENT` |

### Candidate 1: HS→DNp15

Sensory modality is horizontal visual motion. Sources are HSN/HSE/HSS; the
selected route has no intermediate neuron. DNp15 is the bilateral output.
Six chemically connected source-target pairs are directly verified. Primary
evidence supports motion responses and a functional direction-control role,
not a calibrated mapping from a NeuroFly readout to yaw.

`NEW_EXPLORATORY_INPUT_MODEL_FEASIBLE`: start at HS-linked input, **after** retinal
motion extraction. A new encoder must declare motion sign, side, population
semantics and dynamics; the looming encoder/LC4 state contract is not an HS
model. Output is identity-resolved DNp15 state/events and a derived bilateral
difference, never force or yaw. `BODY_OUTPUT_NOT_REQUIRED_FOR_FIRST_VALIDATION`.

Evidence backs identities, routes and qualitative function. Encoder, effective
sign/magnitude/normalization/latency and DNp15 dynamics are bounded exploratory
assumptions requiring future preregistration. No numerical parameters are
selected here. Calibrated yaw is high-risk and excluded, not hidden in an
actuator mapping. All G1–G8 pass for this restricted neural probe.

### Candidate 2: LC16→MDN

Sensory modality is visual threat/expansion; the new output dimension would
be backward/directional retreat rather than Giant Fiber execution. The queried
source-output set contains 186 neurons, but its useful subgraph is not yet
defined: the direct LC16→MDN query returned zero rows. No relay is invented.
This does not refute the primary functional pathway.

`EXISTING_NEUROFLY_INPUT_REUSABLE` is conditional on an LC16-specific encoding
audit; existing expansion primitives do not justify importing LC4 gains or
columns. MDN neural output is interpretable once the upstream boundary exists.
`REQUIRES_BOUNDED_BODY_EXTENSION` for a reverse model-space proxy, not validated
walking. The missing relay and locomotor mapping cannot both be silently
assumed. G1 fails for the nominated route; G2/G4/G7 remain unknown and G6 fails.

### Candidate 3: landing pathway

Sensory modality is visual expansion/progressive dark edges. Primary evidence
supports DNp07/DNp10 landing-related activity and behavioral dependence, with
flight-state effects. The proposed source boundary was LPLC3/LPLC4. MaleCNS
returns LPLC4 routes but not the exact LPLC3 label; no alias was verified.
The partial 101-neuron set has 118 LPLC4→output edges. It is not a complete
verified LPLC3/4 circuit.

`NEW_EXPLORATORY_INPUT_MODEL_FEASIBLE` for the visual descriptor does not solve
flight-state gating. `REQUIRES_MAJOR_BIOMECHANICAL_MODEL` for a landing outcome;
neural-only validation could be reconsidered after identity/context review.
G1 fails for the nominated full boundary; G2/G4/G5/G7 remain unknown and G6
fails. LPLC4 support is substantial but does not resolve the missing source
identity or justify a complete landing model.

## Selected MaleCNS motif and deliberate omissions

| Source body | Type/side | Target body | Type/side | Structural count |
| --- | --- | --- | --- | --- |
| 10015 | HSN/R | 11215 | DNp15/R | 138 |
| 10016 | HSE/R | 11215 | DNp15/R | 122 |
| 10023 | HSS/R | 11215 | DNp15/R | 23 |
| 10181 | HSN/L | 12069 | DNp15/L | 126 |
| 10034 | HSE/L | 12069 | DNp15/L | 78 |
| 10419 | HSS/L | 12069 | DNp15/L | 14 |

Counts document topology only; they neither weight model drive nor assay
aggregation. Eight nodes and six selected edges are a **pathway motif**, not
the complete induced graph. The same query returns 13 edges. The other seven
are explicitly retained as excluded evidence in the JSON: HS↔HS links and
DNp15/L→HSS/L feedback. The selected experiment also excludes the wider H2,
inhibitory/disinhibitory network and electrical coupling.

Thus the future probe can test a declared chemical feedforward composition;
it cannot claim the complete biological course-control mechanism, full
rotational-versus-translational discrimination or biological gap-junction
equivalence. Its assumed dynamics must be named as assumptions. Unexpected
behavior of the small motif is not a falsification of the omitted network.

## First bounded validation experiment — future only

Scientific question: how do predeclared bilateral horizontal-motion descriptors
propagate through the verified HS→DNp15 routing motif under explicit,
preregistered exploratory dynamics?

Population: the six HS identities and two DNp15 identities above. Readout:
per-identity states/events, eligible per-source contributions and a model-derived
R−L comparison, not body yaw. No downstream TTM/G1 shortcut is permitted.

Conditions: no motion (explicit control), bilateral matched progressive motion,
right-only and left-only progressive motion, and direction reversal. Before
execution, freeze input schedules, encoding, state dynamics, effective transfer
sign/magnitude/normalization/latency, DNp15 dynamics, dt and horizon. Their values
must not be chosen to induce spikes or visible movement.

Model-independent invariants are verified identities, metadata laterality,
declared ipsilateral routing, causal provenance, absence of count-as-efficacy,
no injected output and deterministic replay. Equal mirrored numerical responses
are expected only if the future model explicitly assumes identical dynamics
and mirrored input; they are not an empirical symmetry claim.

Accept zero, weak, asymmetric or unexpected-but-valid neural response. Acceptance
depends on composition, declared semantics and reproducibility, not response
size or motion. No body state, scenario UI or steering extension is required
for this first slice.

## Infrastructure and roadmap fit

Reuse identity-resolved machinery, deterministic step conventions and
content-addressed artifact/replay patterns where scientifically compatible.
Existing v1 candidate loaders and DNp01/scenario validators are circuit-specific;
do not relabel HS/DNp15 records as historical v1 fixtures. A new bounded contract
is necessary. Generic telemetry infrastructure is leverage, not a reason to
pretend an API, sensory encoder or embodied output already exists.

The current body has fixed +Z heading and common-mode planar translation, no
yaw or validated force/contact mechanics. Future steering needs a separate
bounded body/output contract. The selected neural dimension could eventually
support Obstacle Course or Changing World; those remain roadmap concepts.
Baseline, Light / Dark, Obstacle Course, Resource Search, Adversity / Avoidance
and Changing World taxonomy is preserved. No new world is implemented.

## Machine-readable authority and verification

[Selection record](second_circuit_selection_gate.json):
`second_circuit_selection_gate_v1`, inner canonical JSON SHA-256/ID
`435ee01693ec0b4b1ad5a8547e77f865c43743cfa56d9c3dd2055a6a87b6ed41`.
Tracked pretty-printed wrapper: 134,108 bytes; canonical inner record: 69,069
bytes. The wrapper's `selection_id`
hashes the inner `selection`, using existing sorted-key, compact canonical
JSON conventions. It has no production runtime dependency.

The embedded `second_circuit_candidate_contract_v1` is conceptual governance,
not executable scenario configuration. Query responses are bounded derived
metadata, not large source connectome datasets. No source archive, raw traces,
local absolute path, credential, candidate simulation, fitting or sensitivity
sweep is included. Five focused tests validate canonical identity, unchanged v1
authority, query hashes, classifications/references, actual selected boundary,
no structural efficacy, controls and absence of runtime dependence.

The post-edit five-artifact replay round also passed unchanged: CLI wall times
were 5.786 s (7O), 3.189 s (8C), 6.731 s (13B), 15.279 s (corrected 16) and
17.949 s (18). Timing is diagnostic only and not part of artifact identities.

Phase 24 validation passed: five focused tests; **1,040 full Python tests**,
one existing deselection and two dependency deprecation warnings in 576.86 s;
**53 frontend tests**; Ruff check and format check, frontend lint/typecheck/build
and `git diff --check`. Both five-artifact replay rounds preserve canonical
identities/results. Only this document, the selection JSON, its isolated tests
and the minimal Project Context addition are changed. No commit/push.

Exactly one next step: implement one **preregistered backend neural-only
HS→DNp15 feedforward validation slice**, freezing assumptions before execution
and accepting genuine null results. No gain-targeting or body-yaw implementation
is recommended as part of that slice.
