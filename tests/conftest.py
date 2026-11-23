"""Shared pytest configuration for the scenario test levels."""

from __future__ import annotations


def pytest_configure(config) -> None:
    config.addinivalue_line(
        "markers", "integration: builds generated sources or a real FMU"
    )
    config.addinivalue_line(
        "markers", "e2e: runs a packaged FMU through fmpy"
    )
