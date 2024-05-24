"""Test module for ssb_gitconfig."""

import sys
from unittest.mock import Mock, patch

import pytest

from kvakk_git_tools import run


@pytest.mark.parametrize("validate_return,exit_code", [(True, 0), (False, 1)])
@patch("kvakk_git_tools.validate_ssb_gitconfig.validate_git_config")
@patch("kvakk_git_tools.ssb_gitconfig.kvakk_git_tools_package_installed")
def test_run_package_installed(
    mock_package_installed: Mock,
    mock_validate: Mock,
    validate_return: bool,
    exit_code: int,
) -> None:
    # Checks that the program exposes the --validate argument when
    # kvakk-git-tools package is installed and exits with 0/1
    # based on what the validate function returns.
    sys.argv = ["", "--validate"]
    mock_validate.return_value = validate_return
    mock_package_installed.return_value = True
    with pytest.raises(SystemExit) as sys_exit:
        run()
    assert sys_exit.value.code == exit_code


@patch("kvakk_git_tools.ssb_gitconfig.kvakk_git_tools_package_installed")
def test_run_package_not_installed(mock_package_installed: Mock) -> None:
    # Checks that the program does not expose the --validate argument when
    # kvakk-git-tools package is not installed
    mock_package_installed.return_value = False
    sys.argv = ["", "--validate"]
    with pytest.raises(SystemExit) as sys_exit:
        run()
    assert sys_exit.value.code == 2  # Should return 2 unknown argument


@pytest.mark.parametrize("package_installed", [True, False])
@patch("kvakk_git_tools.ssb_gitconfig.main")
@patch("kvakk_git_tools.ssb_gitconfig.kvakk_git_tools_package_installed")
def test_run_package_no_args(
    mock_package_installed: Mock, mock_main: Mock, package_installed: bool
) -> None:
    # Checks that main runs when no args are supplied to the program
    # independent of package installation.
    mock_package_installed.return_value = package_installed
    sys.argv = [""]
    run()
    assert mock_main.called
