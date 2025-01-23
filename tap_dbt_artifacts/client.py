"""Custom client handling, including DbtArtifactsStream base class."""

import abc
import json
from pathlib import Path
from typing import Optional, Iterable

from singer_sdk.streams import Stream


class DbtArtifactsStream(Stream, abc.ABC):
    """Base class for dbtArtifacts streams."""

    @property
    def artifact_path(self) -> str:
        """The file path of the artifact JSON file for this stream."""
        return f"{self.config['dbt_target_dir']}/{self.name}.json"
    
    @staticmethod
    def _listify(node: dict | list, key: str) -> dict | None:
        """Convert nested dictionaries to a list of dictionaries.

        Args:
            data: A dict or list to be processed with nested dictionaries.
            key: The key of the nested dictionaries.

        Returns:
            The data[key] nested dictionaries converted to a list of dictionaries
        """
        # Handle list input by extracting the first element
        if isinstance(node, list):
            node = node[0] if node else None  # Handle empty list safely

        # Raise a TypeError if node is not a dictionary
        if not isinstance(node, dict):
            raise TypeError(f"Expected a dictionary, got: {type(node)}")

        # Convert nested dictionaries to a list of dictionaries
        items = node.get(key)
        if isinstance(items, dict):
            node[key] = list(items.values())

        return node

    def get_records(self, context: Optional[dict] = None) -> Iterable[dict]:
        """Read the artifact file and yield records.

        The optional `context` argument is used to identify a specific slice of the
        stream if partitioning is required for the stream. Most implementations do not
        require partitioning and should ignore the `context` argument.

        Args:
            context: Stream partition or context dictionary (unused in this implementation).

        Yields:
            Individual records to be output by the stream.

        Raises:
            json.JSONDecodeError: If the artifact file is not valid JSON.
        """
        file_path = Path(self.artifact_path)
        if not file_path.exists():
            self.logger.warning(f"Artifact file not found: {file_path}")
            return

        try:
            with file_path.open("r") as file:
                data = json.load(file)
                yield from self.extract_records(data)
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to decode JSON from {file_path}: {e}")
            raise
