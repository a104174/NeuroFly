# NeuroFly

NeuroFly is a planned experimental platform for studying connectome-based
digital agents inspired by the MaleCNS *Drosophila melanogaster* connectome.

The repository is currently in **Phase 0A: minimal Python scientific
foundation**. It contains project metadata, one importable Python package, and
offline quality gates. MaleCNS/neuPrint access, neural dynamics, sensory and
motor modelling, and the frontend have not been implemented yet.

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

The project currently has no runtime dependencies. Keep credentials, virtual
environments, caches, and future derived data out of Git.
