"""Stream classes for tap-dbt-artifacts."""

from collections.abc import Iterable
from pathlib import Path
from typing import ClassVar

from tap_dbt_artifacts.client import DbtArtifactsStream

SCHEMAS_DIR = Path(__file__).parent / "schemas"


class RunResultsStream(DbtArtifactsStream):
    """Stream for run_results.json."""

    name: ClassVar[str] = "run_results"
    primary_keys: ClassVar[list[str]] = ["invocation_id", "unique_id"]
    replication_key: ClassVar[str] = "generated_at"
    schema_filepath: ClassVar[Path] = SCHEMAS_DIR / "run-results.schema.json"

    def extract_records(self, data: dict) -> Iterable[dict]:
        """Extract records from the artifact JSON.

        Child classes must implement this to yield individual records.

        Args:
            data: Parsed JSON content of the run results artifact.

        Yields:
            Individual records to be output by the stream.
        """
        # Extract required fields from metadata
        metadata = data.get("metadata", {})
        invocation_id = metadata.get("invocation_id")
        generated_at = metadata.get("generated_at")

        # Extract top-level keys
        results = data.get("results", [])
        elapsed_time = data.get("elapsed_time", 0)
        args = data.get("args", {})

        # Yield each result record
        for result in results:
            unique_id = result.get("unique_id")

            record = {
                "invocation_id": invocation_id,
                "unique_id": unique_id,
                "generated_at": generated_at,
                "metadata": metadata,
                "results": result,
                "elapsed_time": elapsed_time,
                "args": args,
            }

            yield record


class ManifestStream(DbtArtifactsStream):
    """Stream for manifest.json."""

    name: ClassVar[str] = "manifest"
    primary_keys: ClassVar[list[str]] = ["invocation_id"]
    replication_key: ClassVar[str] = "generated_at"
    schema_filepath: ClassVar[Path] = SCHEMAS_DIR / "manifest.schema.json"

    def extract_records(self, data: dict) -> Iterable[dict]:
        """Extract records from the manifest.json file.

        Args:
            data: Parsed JSON content of the manifest artifact.

        Yields:
            Individual records to be output by the stream.
        """
        # Extract required fields from metadata
        metadata = data.get("metadata", {})
        invocation_id = metadata.get("invocation_id")
        generated_at = metadata.get("generated_at")

        # Define top-level keys
        top_level_keys = [
            "nodes",
            "sources",
            "macros",
            "docs",
            "exposures",
            "metrics",
            "groups",
            "selectors",
            "disabled",
            "saved_queries",
            "semantic_models",
            "unit_tests",
        ]

        # Extract mappings
        parent_map = data.get("parent_map", {})
        children_map = data.get("child_map", {})
        group_map = data.get("group_map", {})

        # Yield records for each top-level key
        for key in top_level_keys:
            # Initialize record
            record = {
                "invocation_id": invocation_id,
                "unique_id": None,
                "generated_at": generated_at,
                "metadata": metadata,
            }

            # Extract items for each key
            try:
                items = data.get(key, {}).values()
            except AttributeError:
                items = []

            if len(items) == 0:
                record.update({key: {}})
                yield record

            for item in items:
                # Convert columns key to a list of dictionaries
                parsed_item = self._listify(item, ["columns"])

                # Get the unique_id of each item
                unique_id = parsed_item.get("unique_id")

                # Get parent and children nodes if item is a node or source
                if key in ("nodes", "sources"):
                    parents = parent_map.get(unique_id, [])
                    children = children_map.get(unique_id, [])
                    parsed_item["parents"] = parents
                    parsed_item["children"] = children

                # Get resources if item is a group
                if key == "groups":
                    resources = group_map.get(unique_id, [])
                    parsed_item["resources"] = resources

                # Build and yield the record
                record.update(
                    {
                        "unique_id": unique_id,
                        key: parsed_item,
                    }
                )

                yield record


class CatalogStream(DbtArtifactsStream):
    """Stream for catalog.json."""

    name: ClassVar[str] = "catalog"
    primary_keys: ClassVar[list[str]] = ["invocation_id", "unique_id"]
    replication_key: ClassVar[str] = "generated_at"
    schema_filepath: ClassVar[Path] = SCHEMAS_DIR / "catalog.schema.json"

    def extract_records(self, data: dict) -> Iterable[dict]:
        """Extract records from the catalog.json file.

        Args:
            data: Parsed JSON content of the catalog artifact.

        Yields:
            Individual records to be output by the stream.
        """
        # Extract required fields from metadata
        metadata = data.get("metadata", {})
        invocation_id = metadata.get("invocation_id")
        generated_at = metadata.get("generated_at")

        # Define top-level keys
        top_level_keys = ["nodes", "sources"]

        # Yield records for each top-level key
        for key in top_level_keys:
            # Extract items for each key
            try:
                items = data.get(key, {}).values()
            except AttributeError:
                items = []

            errors = data.get("errors")

            for item in items:
                # Convert columns and stats key to lists of dictionaries
                parsed_item = self._listify(item, ["columns", "stats"])

                # Get the unique_id of each item
                unique_id = parsed_item.get("unique_id")

                # Build and yield the record
                record = {
                    "invocation_id": invocation_id,
                    "unique_id": unique_id,
                    "generated_at": generated_at,
                    "metadata": metadata,
                    key: parsed_item,
                    "errors": errors,
                }

                yield record


class SourcesStream(DbtArtifactsStream):
    """Stream for sources.json."""

    name: ClassVar[str] = "sources"
    primary_keys: ClassVar[list[str]] = ["invocation_id", "unique_id"]
    replication_key: ClassVar[str] = "generated_at"
    schema_filepath: ClassVar[Path] = SCHEMAS_DIR / "sources.schema.json"

    def extract_records(self, data: dict) -> Iterable[dict]:
        """Extract records from the sources.json file.

        Args:
            data: Parsed JSON content of the sources artifact.

        Yields:
            Individual records to be output by the stream.
        """
        # Extract required fields from metadata
        metadata = data.get("metadata", {})
        invocation_id = metadata.get("invocation_id")
        generated_at = metadata.get("generated_at")

        # Extract top-level keys
        results = data.get("results", [])
        elapsed_time = data.get("elapsed_time", 0)

        # Yield each result record
        for result in results:
            unique_id = result.get("unique_id")

            record = {
                "invocation_id": invocation_id,
                "unique_id": unique_id,
                "generated_at": generated_at,
                "metadata": metadata,
                "results": result,
                "elapsed_time": elapsed_time,
            }

            yield record
