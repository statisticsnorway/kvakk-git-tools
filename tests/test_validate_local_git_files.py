"""Test module for validate_ssb_gitignore."""

from kvakk_git_tools.validate_ssb_local_git_files import _validate_local_git_files
from pathlib import Path


def test_validate_git_config_equal() -> None:
    """Test the functionality of the `validate_gitignore()` function."""
    gitignore_path = Path("./tests/test_files/gitignore.test")
    gitattributes_path = Path("./tests/test_files/gitattributes.test")

    assert _validate_local_git_files(gitignore_path, gitattributes_path)
