"""Offline smoke tests for the Phase 0 Python package foundation."""


def test_neurofly_package_imports() -> None:
    import neurofly

    assert neurofly.__doc__
