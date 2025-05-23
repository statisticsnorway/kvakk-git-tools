"""Test module for validate_ssb_gitconfig."""

from unittest.mock import MagicMock

import pytest

from kvakk_git_tools.ssb_gitconfig import Platform, PlatformName
from kvakk_git_tools.validate_ssb_gitconfig import _validate_platform_git_config


def _mock_platform_name(platform_name: str | PlatformName) -> Platform:
    """This helper function returns a Platform object with a mocked name."""
    detected_platform = Platform()
    if isinstance(platform_name, str):
        detected_platform.name = MagicMock(return_value=PlatformName[platform_name])
    else:
        detected_platform.name = MagicMock(return_value=platform_name)
    return detected_platform


def test_validate_git_config_equal() -> None:
    """Test the functionality of the `validate_platform_git_config()` function with all supported platforms listed in the `PlatformName` enum.

    For each platform, the corresponding recommended git config file is passed along
    with the platform to the `validate_platform_git_config()` function.
    When the platform is supported, the function should return True, indicating that the
    configuration file is valid.
    When the platform is not supported, the function should return False, since there is
    no configuration file to compare against.
    """
    platform_enums = PlatformName.__members__.values()
    for platform_enum in platform_enums:
        detected_platform = _mock_platform_name(platform_enum)
        git_config_path = (
            f"kvakk_git_tools/recommended/gitconfig-{detected_platform.name().value}"
        )

        assert (
            _validate_platform_git_config(git_config_path, detected_platform)
            is detected_platform.is_supported()
        )


@pytest.mark.parametrize("platform_name", ["DAPLA_LAB", "DAPLA"])
def test_validate_git_config_with_extra_fields(platform_name: str) -> None:
    """Test the functionality of `validate_platform_git_config()` on a configuration file with extra fields.

    Test that a git configuration with additional fields on top
    of the recommended setup for a specific platform is considered valid by `validate_platform_git_config()`.
    """
    detected_platform = _mock_platform_name(platform_name)
    git_config_path = f"tests/test_files/config_with_extra_{platform_name.lower()}.test"
    assert _validate_platform_git_config(git_config_path, detected_platform)


@pytest.mark.parametrize("platform_name", ["DAPLA_LAB", "DAPLA"])
def test_validate_git_config_not_equal(platform_name: str) -> None:
    """Test the functionality of `validate_platform_git_config()` with an invalid configuration file.

    This function tests that the `validate_platform_git_config()` function returns False when
    called with a configuration file that does not match the recommendations for the detected platform.
    """
    detected_platform = _mock_platform_name(platform_name)
    git_config_path = (
        f"kvakk_git_tools/recommended/gitconfig-{PlatformName.PROD_LINUX.value}"
    )
    assert not _validate_platform_git_config(git_config_path, detected_platform)


@pytest.mark.parametrize("platform_name", ["DAPLA_LAB", "DAPLA"])
def test_validate_git_config_empty_file(platform_name: str) -> None:
    """Test the functionality of `validate_platform_git_config()` with an empty configuration file.

    This function tests that the `validate_platform_git_config()` function returns False when called
    with an empty configuration file.
    """
    detected_platform = _mock_platform_name(platform_name)
    git_config_path = "tests/test_files/empty_config.test"
    assert not _validate_platform_git_config(git_config_path, detected_platform)


@pytest.mark.parametrize("platform_name", ["DAPLA_LAB", "DAPLA"])
def test_validate_git_config_no_file(platform_name: str) -> None:
    """Test the functionality of `validate_platform_git_config()` with a non-existent configuration file.

    This function tests that the `validate_platform_git_config()` function returns False when called
    with a non-existent configuration file.
    """
    detected_platform = _mock_platform_name(platform_name)
    git_config_path = "fake/file/path/no_file.fake"
    with pytest.raises(FileExistsError) as fnf:
        _validate_platform_git_config(git_config_path, detected_platform)
    assert str(fnf.value) == "File: fake/file/path/no_file.fake does not exist!"


@pytest.mark.parametrize("platform_name", ["DAPLA_LAB", "DAPLA"])
def test_verify_configuration_difference_fully_configured(platform_name: str) -> None:
    """Test case to verify that the fully configured Git file returns True."""
    detected_platform = _mock_platform_name(platform_name)
    assert (
        _validate_platform_git_config(
            f"tests/test_files/fully_configured_git_{platform_name.lower()}.test",
            detected_platform,
        )
        is True
    )


@pytest.mark.parametrize("platform_name", ["DAPLA_LAB", "DAPLA"])
def test_verify_configuration_difference_partial_user_configuration(
    platform_name: str,
) -> None:
    """Test case to verify that a partially configured Git file returns False."""
    detected_platform = _mock_platform_name(platform_name)
    assert (
        _validate_platform_git_config(
            f"tests/test_files/partial_user_configuration_{platform_name.lower()}.test",
            detected_platform,
        )
        is False
    )
