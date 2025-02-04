"""Tests standard tap features using the built-in SDK tests library."""

from singer_sdk.testing import get_tap_test_class

from tap_dbt_artifacts.tap import TapDbtArtifacts

SAMPLE_CONFIG = {
    "dbt_target_dir": "target",
}

# Run standard built-in tap tests from the SDK:
TestTapStackExchange = get_tap_test_class(
    tap_class=TapDbtArtifacts,
    config=SAMPLE_CONFIG,
    include_stream_attribute_tests=False,
)
