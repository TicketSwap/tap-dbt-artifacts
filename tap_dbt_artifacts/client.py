"""Custom client handling, including DbtArtifactsStream base class."""

from __future__ import annotations

import json
import typing
from pathlib import Path

from singer_sdk.streams import Stream

if typing.TYPE_CHECKING:
    from collections.abc import Iterable

class DbtArtifactsStream(Stream):
    """Base class for dbtArtifacts streams."""

    @property
    def artifact_path(self) -> str:
        """The file path of the artifact JSON file for this stream."""
        return f"{self.config['dbt_target_dir']}/{self.name}.json"

    @staticmethod
    def _listify(node: dict | list, keys: list[str]) -> dict | None:
        """Convert nested dictionaries to a list of dictionaries.

        Args:
            node: A dict or list to be processed with nested dictionaries.
            keys: The key of the nested dictionaries.

        Returns:
            The node[key] nested dictionaries converted to a list of dictionaries
        """
        # Handle list input by extracting the first element
        if isinstance(node, list):
            node = node[0] if node else None  # Handle empty list safely

        # Raise a TypeError if node is not a dictionary
        if not isinstance(node, dict):
            exception_msg = f"Expected a dictionary, got: {type(node)}"
            raise TypeError(exception_msg)

        # Convert nested dictionaries to a list of dictionaries
        for key in keys:
            items = node.get(key)
            if isinstance(items, dict):
                node[key] = list(items.values())

        return node

    def get_records(self, _context: dict | None = None) -> Iterable[dict]:
        """Read the artifact file and yield records.

        The optional `context` argument is used to identify a specific slice of the
        stream if partitioning is required for the stream. Most implementations do not
        require partitioning and should ignore the `context` argument.

        Args:
            _context: Stream partition or context dictionary (unused).

        Yields:
            Individual records to be output by the stream.

        Raises:
            json.JSONDecodeError: If the artifact file is not valid JSON.
        """
        file_path = Path(self.artifact_path)
        if not file_path.exists():
            warning_msg = f"Artifact file not found: {file_path}"
            self.logger.warning(warning_msg)
            return

        try:
            with file_path.open("r") as file:
                data = json.load(file)
                yield from self.extract_records(data)
        except json.JSONDecodeError as e:
            exception_msg = f"Failed to decode JSON from {file_path}: {e}"
            self.logger.exception(exception_msg)
            raise
