# NeuroFly

NeuroFly is a planned experimental platform for studying connectome-based
digital agents inspired by the MaleCNS *Drosophila melanogaster* connectome.

The repository is currently in **Phase 1A: reproducible MaleCNS data access**.
It can authenticate to Janelia neuPrint, acquire and validate one deliberately
small candidate-circuit snapshot, and export transparent derived data. It does
not implement neural dynamics, sensory or motor modelling, behaviour, an API,
or a frontend.

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
