"""This module provides functions for validating SSB Git local files."""

import sys
from pathlib import Path

def _read_local_git_file(gitignore_path: Path) -> list[str]:
  lines = []
  with open(gitignore_path, 'r', encoding='UTF-8') as file:
    while line := file.readline():
      stripped_line = line.rstrip()
      if not stripped_line.startswith('#'):
          lines.append(stripped_line)
  return lines

def validate_local_git_files(cwd: Path = Path()) -> bool:
    """Validate the local Git files.

    Args:
        cwd: The path to the current working directory in which to find the local git files.

    Returns
        bool: True if the local git files are valid, False otherwise. See: `_validate_local_git_files`
    """
    gitignore_path = cwd.joinpath(".gitignore")
    gitattributes_path = cwd.joinpath(".gitattributes")
    return _validate_local_git_files(gitignore_path, gitattributes_path)

def _validate_local_git_files(gitignore_path: Path, gitattributes_path: Path) -> bool:
    """Validates local Git files (.gitattributes and .gitignore) against recommended versions.

    Args:
        git_config_path: The path to the local Git configuration file.

    Returns:
        bool: True if the gitignore file at least contains all the configuration from the recommended file, False otherwise.
    """
    if not gitignore_path.is_file():
        raise FileExistsError(f"File: {gitignore_path} does not exist!")

    if not gitattributes_path.is_file():
        raise FileExistsError(f"File: {gitattributes_path} does not exist!")

    if sys.version_info.major == 3 and sys.version_info.minor < 10:
        import pkg_resources
        relative_path = pkg_resources.resource_stream(__package__)
    else:
        from importlib.resources import files
        relative_path = files(__package__)

    ssb_recommended_ignore_file_path = relative_path.joinpath("recommended/gitignore")
    ssb_recommended_attributes_file_path = relative_path.joinpath("recommended/gitattributes")
    ssb_recommended_ignore = _read_local_git_file(ssb_recommended_ignore_file_path)
    ssb_recommended_attributes = _read_local_git_file(ssb_recommended_attributes_file_path)
    local_ignore = _read_local_git_file(gitignore_path)
    local_attributes = _read_local_git_file(gitattributes_path)

    return all(
        line in local_ignore for line in ssb_recommended_ignore
    ) and all(
        line in local_attributes for line in ssb_recommended_attributes
    )
