"""Test module for validate_ssb_gitconfig."""
from unittest.mock import MagicMock

from kvakk_git_tools.ssb_gitconfig import Platform, PlatformName
from kvakk_git_tools.validate_ssb_gitconfig import _validate_platform_git_config


def _mock_platform_name(platform_name: PlatformName) -> MagicMock:
    """This helper function returns a Platform object with a mocked name."""
    detected_platform = Platform()
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


def test_validate_git_config_not_equal() -> None:
    """Test the functionality of `validate_platform_git_config()` with an invalid configuration file.

    This function tests that the `validate_platform_git_config()` function returns False when
    called with a configuration file that does not match the recommendations for the detected platform.
    """
    detected_platform = _mock_platform_name(PlatformName.DAPLA)
    git_config_path = (
        f"kvakk_git_tools/recommended/gitconfig-{PlatformName.PROD_LINUX.value}"
    )
    assert not _validate_platform_git_config(git_config_path, detected_platform)


def test_validate_git_config_empty_file() -> None:
    """Test the functionality of `validate_platform_git_config()` with an empty configuration file.

    This function tests that the `validate_platform_git_config()` function returns False when called
    with an empty configuration file.
    """
    detected_platform = _mock_platform_name(PlatformName.DAPLA)
    git_config_path = "tests/test_files/empty_config.test"
    assert not _validate_platform_git_config(git_config_path, detected_platform)


def test_validate_git_config_no_file() -> None:
    """Test the functionality of `validate_platform_git_config()` with a non-existent configuration file.

    This function tests that the `validate_platform_git_config()` function returns False when called
    with a non-existent configuration file.
    """
    detected_platform = _mock_platform_name(PlatformName.DAPLA)
    git_config_path = "fake/file/path/no_file.fake"
    assert not _validate_platform_git_config(git_config_path, detected_platform)
