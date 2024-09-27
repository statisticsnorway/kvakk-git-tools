"""This module provides functions for validating SSB Git configuration."""

import configparser
import sys
from pathlib import Path

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

    ssb_config = configparser.ConfigParser()

    # If python version is older than 3.10 use stdlib module which is now deprecated.
    if sys.version_info.major == 3 and sys.version_info.minor < 10:
        import pkg_resources

        with pkg_resources.resource_stream(
            __package__, ssb_recommended_config_file_path
        ) as ssb_config_file:
            ssb_config.read_string(ssb_config_file.read().decode("utf-8"))
    else:
        from importlib.resources import files

        with files(__package__).joinpath(ssb_recommended_config_file_path).open(
            "rb"
        ) as ssb_config_file:
            ssb_config.read_string(ssb_config_file.read().decode("utf-8"))

    with open(git_config_path, "r") as local_config_file:
        local_config = configparser.ConfigParser()
        local_config.read_string(local_config_file.read())

    ssb_config = {
        section: dict(ssb_config.items(section)) for section in ssb_config.sections()
    }

    local_config = {
        section: dict(local_config.items(section))
        for section in local_config.sections()
    }

    # If the [user] section exists ensure that both
    # name and email fields are set
    if "user" in local_config and not all(
        key in local_config["user"] for key in ("name", "email")
    ):
        return False

    return all(
        _check_config(value, local_config, section, key)
        for section in ssb_config
        for key, value in ssb_config[section].items()
    )


def _check_config(
    expected_value: str,
    actual_conf: dict[str, dict[str, str]],
    section: str,
    key: str,
) -> bool:
    """Ensure that the section and key exist in the configuraton
    and that the value equals the expected value."""
    if section not in actual_conf:
        return False
    if key not in actual_conf[section]:
        return False

    return expected_value == actual_conf[section][key]
