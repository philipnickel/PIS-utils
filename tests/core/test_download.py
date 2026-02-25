"""Tests for download utilities."""

from unittest.mock import Mock, patch

import pytest
import requests

from pis_utils.core import download_file


def test_download_file_success(tmp_path):
    """Test successful file download."""
    dest = tmp_path / "test_file.txt"
    test_content = b"Hello, World!"

    # Mock the requests.get response
    mock_response = Mock()
    mock_response.headers = {"content-length": str(len(test_content))}
    mock_response.iter_content = Mock(return_value=[test_content])
    mock_response.__enter__ = Mock(return_value=mock_response)
    mock_response.__exit__ = Mock(return_value=False)

    with patch("requests.get", return_value=mock_response):
        download_file("https://example.com/file.txt", dest)

    assert dest.exists()
    assert dest.read_bytes() == test_content


def test_download_file_custom_description(tmp_path):
    """Test download with custom description."""
    dest = tmp_path / "test_file.txt"
    test_content = b"Test"

    mock_response = Mock()
    mock_response.headers = {"content-length": str(len(test_content))}
    mock_response.iter_content = Mock(return_value=[test_content])
    mock_response.__enter__ = Mock(return_value=mock_response)
    mock_response.__exit__ = Mock(return_value=False)

    with patch("requests.get", return_value=mock_response):
        download_file(
            "https://example.com/file.txt", dest, description="Custom download"
        )

    assert dest.exists()


def test_download_file_http_error(tmp_path):
    """Test download with HTTP error."""
    dest = tmp_path / "test_file.txt"

    mock_response = Mock()
    mock_response.raise_for_status = Mock(
        side_effect=requests.HTTPError("404 Not Found")
    )
    mock_response.__enter__ = Mock(return_value=mock_response)
    mock_response.__exit__ = Mock(return_value=False)

    with (
        patch("requests.get", return_value=mock_response),
        pytest.raises(requests.HTTPError),
    ):
        download_file("https://example.com/missing.txt", dest)


def test_download_file_no_content_length(tmp_path):
    """Test download without content-length header."""
    dest = tmp_path / "test_file.txt"
    test_content = b"No length"

    mock_response = Mock()
    mock_response.headers = {}  # No content-length
    mock_response.iter_content = Mock(return_value=[test_content])
    mock_response.__enter__ = Mock(return_value=mock_response)
    mock_response.__exit__ = Mock(return_value=False)

    with patch("requests.get", return_value=mock_response):
        download_file("https://example.com/file.txt", dest)

    assert dest.exists()
    assert dest.read_bytes() == test_content
