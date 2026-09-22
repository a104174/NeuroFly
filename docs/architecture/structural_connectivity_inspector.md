# Bounded structural connectivity inspector (Phase 5I)

Phase 5I projects only existing directed CircuitContract edges between the
fixed Phase 5G/5H morphology sample:

| body ID | type | source side | node index |
|---:|---|:---:|---:|
| 12032 | LC4 | L | 3 |
| 16128 | LC4 | R | 16 |
| 11498 | LPLC2 | L | 2 |
| 14465 | LPLC2 | R | 12 |
| 10010 | DNp01 | L | 1 |
| 10001 | DNp01 | R | 0 |

The selection is exactly `LC4/LPLC2 -> DNp01`; all other edges in the wider
CircuitContract are excluded. The projection reads the local, validated
`looming_giant_fiber_v1` snapshot. Its provenance contains the original
`neurons.jsonl` and `connections.jsonl` SHA-256 hashes, dataset, candidate,
endpoint, and acquisition metadata. The snapshot loader verifies both hashes,
record counts, pinned content invariants, and body-level type consistency. The
projection validates the six expected `(body_id, node_index, type, side,
status)` identities before returning data. It does not create a new source
identity from the contract's existing file digests. It also pins those existing
source-file digests and acquisition metadata, so a different otherwise-valid
snapshot cannot silently replace this projection's source:

- `neurons.jsonl`: `00fcba6a1cb3ccd650610bce61de6ce017f4b7ab472cfc9339c5d5247cad264e`
- `connections.jsonl`: `f7e55419d8f18a885f5ebcffa99ec8bf117d055593c0285c61def47020ae340a`

The current real projection, ordered by `(pre_node_index, post_node_index)`,
is:

| pre | post | structural weight |
|---|---|---:|
| LPLC2 11498 (L, index 2) | DNp01 10010 (L, index 1) | 2 |
| LC4 12032 (L, index 3) | DNp01 10010 (L, index 1) | 62 |
| LPLC2 14465 (R, index 12) | DNp01 10001 (R, index 0) | 21 |
| LC4 16128 (R, index 16) | DNp01 10001 (R, index 0) | 65 |

The bounded projection has 4 edges and total structural weight 150 (LC4 127;
LPLC2 23). These counts describe only the fixed six-body projection and do
not estimate connectivity for either full population. `structural_weight` is
the unmodified neuPrint `ConnectsTo.weight` structural count; it is not
physiological efficacy or a simulation parameter.

## Read-only API

Set `NEUROFLY_CIRCUIT_CONTRACT_ROOT` to the local
`data/derived/malecns/looming_giant_fiber_v1` snapshot directory alongside the
existing experiment artifact root. The explicit setting is fail-closed:
without it, the connectivity route returns a sanitized 503 response. The
read-only endpoint is:

```text
GET /api/v1/connectivity/phase5i_six_body_visual_to_dnp01_v1
```

It returns `malecns_structural_connectivity_v1`; an unsupported projection
returns 404, a missing local snapshot returns 404, a malformed or hash-invalid
snapshot returns 409, and a fixed identity/provenance mismatch returns 409.
Only GET is registered. The projection calls only the local
`load_circuit_contract`; it never queries neuPrint, downloads morphology, or
runs simulation code.

## Schematic overlay

The browser validates the fixed schema, sample identities, endpoint roles,
direction, canonical order, positive integer structural weights, unique edge
pairs, source hashes, and aggregate sums before rendering. Source edge records
remain separate from presentation connector records.

For each body, the presentation anchor is the center of that body's raw
source-coordinate bounds transformed through the existing shared
`malecns_six_body_morphology_view_v1`. A straight line connects the pre and
post anchors. The anchor and path are presentation geometry only; the artifact
contains no synapse locations, and the lines do not locate synaptic contacts
or describe axon/dendrite trajectories. Text reads `pre -> post`; no 3D arrow
implies timing or signal propagation.

Lines have constant width and do not encode structural weight. Selecting a
body highlights its incident connectors and lists the corresponding incoming
or outgoing relationships with textual direction, source sides, node indices,
and structural weight. Unrelated edges are visually de-emphasized. Selecting a
morphology component leaves the body-level edge identities unchanged. Hiding
either endpoint hides that connector while its source edge remains in the
textual audit. The toggle is off initially. No activity, pulse, glow, or
simulation telemetry appears in this layer.

Morphology source coordinates, hashes, components, and the shared view
transform remain unchanged. The overlay is one reusable read-only primitive
for a future Scientific Cockpit; it does not add a dashboard, playback
integration, or physiological interpretation.
