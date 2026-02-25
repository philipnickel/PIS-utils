"""File download utilities with progress bars."""

from pathlib import Path

import requests
from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    TextColumn,
    TransferSpeedColumn,
)

from pis_utils.core.console import console


def download_file(url: str, dest: Path, description: str | None = None) -> None:
    """
    Download a file from a URL with a Rich progress bar.

    Args:
        url: The URL to download from
        dest: The destination file path
        description: Optional description for the progress bar (defaults to filename)

    Raises:
        requests.HTTPError: If the HTTP request fails
        requests.Timeout: If the request times out
        requests.RequestException: For other request-related errors

    Example:
        >>> download_file(
        ...     "https://example.com/file.zip",
        ...     Path("/tmp/file.zip"),
        ...     "Downloading installer"
        ... )
    """
    if description is None:
        description = f"Downloading {dest.name}"

    with requests.get(url, stream=True, allow_redirects=True, timeout=60) as r:
        r.raise_for_status()
        total = int(r.headers.get("content-length", 0))

        with Progress(
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            DownloadColumn(),
            TransferSpeedColumn(),
            console=console,
        ) as progress:
            task = progress.add_task(description, total=total or None)

            with open(dest, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
                    progress.advance(task, len(chunk))


__all__ = ["download_file"]
