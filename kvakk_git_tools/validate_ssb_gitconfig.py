"""This module provides functions for validating SSB Git configuration."""

from pathlib import Path

import pkg_resources

from kvakk_git_tools.ssb_gitconfig import Platform


def validate_git_config() -> bool:
    """Validates the local Git configuration file against the recommended Git configuration file for the current platform.

    Returns True if the two files are the same, False otherwise.

    Returns:
        bool: True if the local Git configuration file matches the recommended Git configuration file, False otherwise.
    """
    git_config_path = Path.home() / ".gitconfig"
    detected_platform = Platform()
    return _validate_platform_git_config(git_config_path, detected_platform)


def _validate_platform_git_config(
    git_config_path: Path, detected_platform: Platform
) -> bool:
    """Validates a local Git configuration file against a recommended Git configuration file for a given platform.

    Returns True if the two files are the same, False otherwise.

    Args:
        git_config_path: The path to the local Git configuration file.
        detected_platform: The platform that the script is running on.

    Returns:
        bool: True if the local Git configuration file matches the recommended Git configuration file, False otherwise.
    """
    if detected_platform.is_unsupported():
        return False

    if not Path(git_config_path).is_file():
        raise FileExistsError(f"File: {git_config_path} does not exist!")

    ssb_recommended_config_file_path = (
        f"recommended/gitconfig-{detected_platform.name().value}"
    )

    with pkg_resources.resource_stream(
        __package__, ssb_recommended_config_file_path
    ) as ssb_config_file:
        ssb_config_contents = ssb_config_file.read()
        ssb_config_contents_str = ssb_config_contents.decode("utf-8")

    with open(git_config_path) as local_config_file:
        local_config_contents = local_config_file.read()

    ssb_config_lines = ssb_config_contents_str.split("\n")
    local_config_lines = local_config_contents.split("\n")
    if ssb_config_lines == local_config_lines:
        return True
    else:
        rest = [line for line in local_config_lines if line not in ssb_config_lines]
        return _verify_configuration_difference(rest)


def _verify_configuration_difference(rest: list[str]) -> bool:
    """Checks that the difference in configuration is only [user], name, and email.

    Args:
        rest (list[str]): A list containing the elements to check.

    Returns:
        bool: True if the difference contains only [user], name, and email settings. False otherwise.
    """
    if len(rest) != 3:
        return False

    # Check that the rest of the configuration contains [user], name, and email in the expected order
    if "[user]" in rest[0] and "\tname =" in rest[1] and "\temail =" in rest[2]:
        return True

    return False
