"""DbtArtifacts entry point."""

from __future__ import annotations

from tap_dbt_artifacts.tap import TapDbtArtifacts

TapDbtArtifacts.cli()
