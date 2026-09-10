# NeuroFly

NeuroFly is a planned experimental platform for studying connectome-based
digital agents inspired by the MaleCNS *Drosophila melanogaster* connectome.

The repository is currently in **Phase 1D-B: bounded MaleCNS body-to-visual-space
feasibility validation**. It can acquire a deliberately small candidate-circuit
snapshot from Janelia neuPrint, then load, verify, and inspect that snapshot
entirely offline. The current audit found no provenance-verifiable body-level
LC4/LPLC2 receptive-field mapping for `male-cns:v1.0`; a deterministic 16-body
sample is recorded, while live input-anatomy validation remains credential
gated. The Phase 1C population-level sensory boundary remains in force. It
does not implement neural dynamics, sensory or motor modelling, behaviour, an
API, or a frontend.

Scientific integrity is a project constraint: future code must distinguish
biological/connectomic data from NeuroFly modelling assumptions. The detailed
project intent and scientific brief are maintained in
[`docs/NeuroFly_Project_Context.md`](docs/NeuroFly_Project_Context.md).

## Development setup

Use Python 3.12.x. From the repository root, create or activate a virtual
environment and install the project with its development tools:

```bash
python -m venv .venv
python -m pip install --editable ".[dev]"
```

The canonical quality commands are:

```bash
python -m pytest
python -m ruff check .
python -m ruff format --check .
```

## MaleCNS Phase 1A

The versioned candidate `looming_giant_fiber_v1` selects every typed `:Neuron`
body with type `LC4`, `LPLC2`, or `DNp01` from the official endpoint
`https://neuprint.janelia.org`, pinned to dataset `male-cns:v1.0`. Acquisition
preserves the complete body-level chemical `ConnectsTo` induced subgraph among
all selected bodies—including reverse, recurrent, same-type, and cross-type
edges—not merely the primary LC4/LPLC2 to DNp01 motif.

Get application credentials from neuPrint and inject them through the normal
environment:

```bash
export NEUPRINT_APPLICATION_CREDENTIALS='your credential from neuPrint'
```

Never commit, print, or serialize this value. The code does not load `.env`
files, and `.env` remains ignored.

Check authentication and the pinned dataset without downloading the circuit:

```bash
python -m neurofly.malecns check-access
```

Acquire, validate, and export the candidate:

```bash
python -m neurofly.malecns snapshot
```

The default output is
`data/derived/malecns/looming_giant_fiber_v1/`, containing deterministically
ordered `neurons.jsonl`, `connections.jsonl`, and `manifest.json`. This derived
path is ignored by Git. Export validates all pinned scientific invariants
before writing, stages all files in a temporary sibling directory, and then
finalizes atomically. It fails if the target already exists; remove the target
explicitly before regenerating so snapshots are never silently mixed or
replaced.

Normal tests remain offline. The authenticated smoke test is opt-in:

```bash
python -m pytest -m integration
```

It skips if `NEUPRINT_APPLICATION_CREDENTIALS` is absent. The ordinary
`python -m pytest` command excludes integration tests.

## Offline circuit contract

Phase 1B separates network-based acquisition from offline consumption. Validate
the default ignored snapshot and print its deterministic structural summary:

```bash
python -m neurofly.malecns inspect-snapshot
```

An alternate snapshot directory can be supplied as the positional argument.
This command requires neither network access nor neuPrint credentials. It
verifies the supported candidate and dataset, required files, SHA-256 hashes,
record counts, biological records, edge endpoints and types, unique body-level
edges, the complete type-pair summary, and the primary LC4/LPLC2 to DNp01
invariants before constructing the circuit contract.

Nodes are ordered by biological `body_id`. Contiguous node indices `0..312`
are a deterministic project implementation convenience; they are not MaleCNS
identifiers. The contract retains all chemical structural edges, including
same-type, reverse-direction, low-weight, and DNp01-originating connections.

The contract and its scientific boundaries are documented in
[`docs/science/circuit_contract.md`](docs/science/circuit_contract.md).

## Sensory boundary and looming benchmark (Phase 1C)

Phase 1C specifies a deterministic, model-neutral looming stimulus using
physical radius, approach velocity, initial distance, visual center, time,
angular size, and angular expansion velocity. It also records literature-grounded
benchmarks for LPLC2 selectivity, LC4/LPLC2 feature separation, and combined
DNp01/Giant Fiber integration. These specifications do not generate neural
inputs or behaviour. See
[`docs/science/sensory_boundary_evidence.md`](docs/science/sensory_boundary_evidence.md).

## MaleCNS receptive-field feasibility (Phase 1D-B)

Phase 1D-B audits the 2026 MaleCNS visual-pathway work, official optic-column
and eye-map resources, and a deterministic sample of 16 real candidate bodies.
No body-keyed LC4 or LPLC2 receptive-field artifact was provenance-verified.
Both populations remain **unresolved**: live body-to-input-anatomy validation
is pending credentials. This is not evidence that MaleCNS body-level mapping
is impossible or fundamentally indefensible. No live body, input-synapse, ROI,
or morphology query was made and no morphology was acquired or healed. See
[`docs/science/receptive_field_feasibility.md`](docs/science/receptive_field_feasibility.md)
for the sample manifest, evidence ledger, limitations, safeguards, and smallest
next phase.

### Scientific semantics and limitation

Neuron annotations and null values are retained as source data. In connection
records, `structural_weight` maps exactly to neuPrint `ConnectsTo.weight`: a
structural synaptic-contact/connectivity count, **not** a physiological or
NeuroFly simulation coupling parameter. Reconstruction statuses such as
`Traced` are database metadata, not physiological states, and predicted versus
consensus neurotransmitter annotations remain separate.

LC4 and LPLC2 are visual projection populations and DNp01/Giant Fiber is the
initial descending endpoint, but these three types are not claimed to be a
complete visual or escape circuit. The acquired `ConnectsTo` graph represents
chemical-connectome structure. Giant Fiber downstream biology also contains
electrical/gap-junction contributions (including circuitry involving TTMn and
PSI), which this snapshot neither invents nor represents.
