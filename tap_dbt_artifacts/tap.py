"""DbtArtifacts tap class."""

from singer_sdk import Stream, Tap
from singer_sdk import typing as th

from tap_dbt_artifacts.streams import (
    CatalogStream,
    ManifestStream,
    RunResultsStream,
    SourcesStream,
)

STREAM_TYPES = [
    RunResultsStream,
    ManifestStream,
    CatalogStream,
    SourcesStream,
]


class TapDbtArtifacts(Tap):
    """DbtArtifacts tap class."""

    name = "tap-dbt-artifacts"

    config_jsonschema = th.PropertiesList(
        th.Property(
            name="dbt_target_dir",
            wrapped=th.StringType,
            required=True,
            default="target",
        ),
    ).to_dict()

    def discover_streams(self) -> list[Stream]:
        """Return a list of discovered streams."""
        return [stream_class(tap=self) for stream_class in STREAM_TYPES]
