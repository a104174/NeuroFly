"""Serving metadata and fresh-process isolation from acquisition imports."""

import os
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_acquisition_requirement_is_optional_and_pinned():
    project = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]
    assert project["dependencies"] == [
        "fastapi>=0.115,<1",
        "numpy>=2,<3",
        "uvicorn>=0.30,<1",
    ]
    assert project["optional-dependencies"]["acquisition"] == ["neuprint-python==0.6.3"]
    readme = (ROOT / "README.md").read_text()
    assert '".[dev,acquisition]"' in readme
    assert '".[acquisition]"' in readme
    assert "missing optional dependency, not corrupt biological" in readme


def test_fresh_serving_processes_never_import_acquisition_packages():
    script = """
import importlib.abc
import sys
import tempfile
from pathlib import Path
class RejectAcquisition(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.')[0] in {'neuprint', 'scipy', 'pyarrow', 'pandas'}:
            raise AssertionError('serving attempted acquisition import')
sys.meta_path.insert(0, RejectAcquisition())
sys.path.insert(0, str(Path.cwd() / 'src'))
from neurofly.http_api import create_app
from fastapi.testclient import TestClient
with tempfile.TemporaryDirectory() as root, TestClient(create_app(root)) as client:
    assert client.get('/health').json()['read_only'] is True
    assert client.get('/ready').status_code == 503
    assert len(client.get('/api/v1/scenarios').json()) == 5
    catalogue = client.get('/api/v1/experiments')
    assert catalogue.status_code == 200
    assert catalogue.json()['count'] == 0
"""
    for _ in range(2):
        result = subprocess.run(
            [sys.executable, "-I", "-B", "-c", script],
            cwd=ROOT,
            env={"PATH": os.defpath},
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stderr
