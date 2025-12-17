"""
Tests for the VANILLA Collection CLI module.

Run with: pytest tests/test_cli.py -v
"""

from unittest.mock import patch

import pytest

from vanilla_collection.cli import _parse_args, main


class TestParseArgs:
    """Tests for argument parsing."""

    def test_default_args(self):
        """Test default argument values."""
        args = _parse_args([])
        assert args.host is None
        assert args.port is None
        assert args.auto_open is None
        assert args.scores is None

    def test_host_arg(self):
        """Test --host argument."""
        args = _parse_args(["--host", "127.0.0.1"])
        assert args.host == "127.0.0.1"

    def test_port_arg(self):
        """Test --port argument."""
        args = _parse_args(["--port", "8080"])
        assert args.port == 8080

    def test_debug_flag(self):
        """Test --debug flag."""
        args = _parse_args(["--debug"])
        assert args.debug is True

    def test_no_debug_flag(self):
        """Test --no-debug flag."""
        args = _parse_args(["--no-debug"])
        assert args.no_debug is True

    def test_debug_and_no_debug_mutually_exclusive(self):
        """Test that --debug and --no-debug are mutually exclusive."""
        with pytest.raises(SystemExit):
            _parse_args(["--debug", "--no-debug"])

    def test_open_flag(self):
        """Test --open flag."""
        args = _parse_args(["--open"])
        assert args.auto_open is True

    def test_no_open_flag(self):
        """Test --no-open flag."""
        args = _parse_args(["--no-open"])
        assert args.auto_open is False

    def test_open_and_no_open_mutually_exclusive(self):
        """Test that --open and --no-open are mutually exclusive."""
        with pytest.raises(SystemExit):
            _parse_args(["--open", "--no-open"])

    def test_scores_arg(self):
        """Test --scores argument."""
        args = _parse_args(["--scores", "/path/to/scores.json"])
        assert args.scores == "/path/to/scores.json"

    def test_combined_args(self):
        """Test multiple arguments together."""
        args = _parse_args(
            [
                "--host",
                "0.0.0.0",
                "--port",
                "3000",
                "--debug",
                "--no-open",
                "--scores",
                "/tmp/scores.json",
            ]
        )
        assert args.host == "0.0.0.0"
        assert args.port == 3000
        assert args.debug is True
        assert args.auto_open is False
        assert args.scores == "/tmp/scores.json"


class TestMain:
    """Tests for the main CLI function."""

    @patch("vanilla_collection.cli.run")
    def test_main_default(self, mock_run):
        """Test main with default arguments."""
        result = main([])
        assert result == 0
        mock_run.assert_called_once()
        call_kwargs = mock_run.call_args[1]
        assert call_kwargs["host"] is None
        assert call_kwargs["port"] is None
        assert call_kwargs["debug"] is None
        assert call_kwargs["auto_open"] is None

    @patch("vanilla_collection.cli.run")
    def test_main_with_host_port(self, mock_run):
        """Test main with host and port."""
        result = main(["--host", "127.0.0.1", "--port", "8080"])
        assert result == 0
        call_kwargs = mock_run.call_args[1]
        assert call_kwargs["host"] == "127.0.0.1"
        assert call_kwargs["port"] == 8080

    @patch("vanilla_collection.cli.run")
    def test_main_with_debug(self, mock_run):
        """Test main with debug flag."""
        result = main(["--debug"])
        assert result == 0
        call_kwargs = mock_run.call_args[1]
        assert call_kwargs["debug"] is True

    @patch("vanilla_collection.cli.run")
    def test_main_with_no_debug(self, mock_run):
        """Test main with no-debug flag."""
        result = main(["--no-debug"])
        assert result == 0
        call_kwargs = mock_run.call_args[1]
        assert call_kwargs["debug"] is False

    @patch("vanilla_collection.cli.run")
    def test_main_with_no_open(self, mock_run):
        """Test main with no-open flag."""
        result = main(["--no-open"])
        assert result == 0
        call_kwargs = mock_run.call_args[1]
        assert call_kwargs["auto_open"] is False

    @patch("vanilla_collection.cli.run")
    def test_main_with_scores_path(self, mock_run):
        """Test main with scores path."""
        result = main(["--scores", "/custom/path/scores.json"])
        assert result == 0
        call_kwargs = mock_run.call_args[1]
        assert call_kwargs["scores_path"] is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
