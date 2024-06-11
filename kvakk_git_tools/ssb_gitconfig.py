#!/usr/bin/env python3
""" This script sets the recommended .gitconfig for the detected platform.

The recommended base git configs are stored in the public git repository
https://github.com/statisticsnorway/kvakk-git-tools.git. The script clones this
repo and selects the base git config based on the detected platform.

If there is an existing .gitconfig file, it is backed up, and the name and email
address are extracted from it and reused.
"""

__version__ = "2.2.3"

import argparse
import getpass
import os
import platform
import shutil
import stat
import subprocess
import sys
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional, Tuple

import pkg_resources


def ping(host: str) -> bool:
    """Returns True if host responds to a ping request."""
    # Option for the number of packets is different on Windows and Linux
    ping_param = "-n" if platform.system() == "Windows" else "-c"

    # Timeout is -w <milliseconds> on Windows, and -W <seconds> on Linux
    timeout_param = "-w" if platform.system() == "Windows" else "-W"
    timeout_value = "1" if platform.system() == "Linux" else "1000"

    # Building the command. Ex: "ping -c 1 google.com"
    command = ["ping", ping_param, "1", timeout_param, timeout_value, host]

    # Fix for python < 3.7, using stdout.
    # Use capture_output=true instead of stdout when python >= 3.7
    return subprocess.run(command, stdout=subprocess.PIPE).returncode == 0


def remove_readonly(func, path, exc_info):
    """Workaround for a bug on Windows https://github.com/python/cpython/issues/87823.

    On Windows the command shutil.rmtree() fails on read-only files. This function,
    used by shutil.rmtree(..., onerror=remove_readonly), is the documented workaround
    described in the issue.
    """
    # Clear the readonly bit and reattempt the removal
    # ERROR_ACCESS_DENIED = 5
    if func not in (os.unlink, os.rmdir) or exc_info[1].winerror != 5:
        raise exc_info[1]
    os.chmod(path, stat.S_IWRITE)
    func(path)


class PlatformName(Enum):
    """Enum representing the platform names. Used in the Platform class."""

    DAPLA = "dapla"
    PROD_LINUX = "prod-linux"
    PROD_WINDOWS_CITRIX = "prod-windows-citrix"
    PROD_WINDOWS_VDI = "prod-windows-vdi"
    ADM_WINDOWS = "adm-windows"
    ADM_MAC = "adm-mac"
    UNKNOWN = "unknown"


class Platform:
    """Class detecting the platform the script is running on."""

    def __init__(self):
        self.linux = False
        self.windows = False
        self.dapla = False
        self.prod_zone = False
        self.adm_zone = False
        self.citrix = False
        self.mac = False

        my_os = platform.system()
        if my_os == "Linux":
            self.linux = True
        elif my_os == "Windows":
            self.windows = True
        elif my_os == "Darwin":
            self.mac = True

        if (
            os.environ.get("DAPLA_REGION") == "DAPLA_LAB"
            or os.environ.get("DAPLA_REGION") == "BIP"
        ):
            self.dapla = True

        if not self.dapla:
            self.prod_zone = ping("sl-jupyter-p.ssb.no")
            if not self.prod_zone:
                self.adm_zone = ping("aw-dc04.ssb.no")
            session_name = os.environ.get("SESSIONNAME")
            self.citrix = session_name is not None and "ICA" in session_name

    def __repr__(self):
        return (
            f"{self.name().name}(linux={self.linux}, "
            f"windows={self.windows}, mac={self.mac}, dapla={self.dapla}, "
            f"adm_zone={self.adm_zone}, prod_zone={self.prod_zone}, "
            f"citrix={self.citrix})"
        )

    def name(self) -> PlatformName:
        if self.prod_zone:
            if self.linux:
                return PlatformName.PROD_LINUX
            if self.windows:
                if self.citrix:
                    return PlatformName.PROD_WINDOWS_CITRIX
                return PlatformName.PROD_WINDOWS_VDI
        if self.dapla:
            return PlatformName.DAPLA
        if self.adm_zone:
            if self.windows:
                return PlatformName.ADM_WINDOWS
            if self.mac:
                return PlatformName.ADM_MAC
        return PlatformName.UNKNOWN

    def is_unsupported(self) -> bool:
        unsupported = [
            PlatformName.PROD_WINDOWS_VDI,
            PlatformName.ADM_WINDOWS,
            PlatformName.ADM_MAC,
            PlatformName.UNKNOWN,
        ]
        return self.name() in unsupported

    def is_supported(self) -> bool:
        return not self.is_unsupported()


class TempDir:
    """Context manager class for creating and cleaning up a temporary directory."""

    def __init__(self, temp_dir: Path) -> None:
        if temp_dir.exists():
            raise RuntimeError(f"The directory {temp_dir} already exist.")
        self.temp_dir = temp_dir

    def __enter__(self):
        self.temp_dir.mkdir(parents=True)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if platform.system() == "Windows":
            # Workaround for bug https://github.com/python/cpython/issues/87823
            shutil.rmtree(self.temp_dir, onerror=remove_readonly)
        else:
            shutil.rmtree(self.temp_dir)


def replace_text_in_file(old_text: str, new_text: str, file: Path) -> None:
    with open(file, "r") as infile:
        filedata = infile.read()
    filedata = filedata.replace(old_text, new_text)
    with open(file, "w", newline="\n") as outfile:
        outfile.write(filedata)


def get_gitconfig_element(element: str) -> Optional[str]:
    cmd = ["git", "config", "--get", element]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, encoding="utf-8")
    return None if result.stdout == "" else result.stdout.strip()


def extract_name_email() -> Tuple[Optional[str], Optional[str]]:
    name = get_gitconfig_element("user.name")
    email = get_gitconfig_element("user.email")
    return name, email


def backup_gitconfig(gitconfig_file: Path) -> bool:
    if gitconfig_file.is_file():
        timestamp_str = datetime.now().strftime("%y%m%d_%H%M%S")
        destination_filename = f".gitconfig_{timestamp_str}"
        print(f"Backup existing .gitconfig to {destination_filename}")

        backup_file = Path.home() / destination_filename
        backup_file.write_bytes(gitconfig_file.read_bytes())
        return True
    return False


def request_name_email() -> Tuple[str, str]:
    print("Git needs to know your name (first name and surname) and email address.")
    name = input("Enter name: ")
    email = input("Enter email: ")
    return name, email


def set_base_config(pl: Platform, test: bool) -> str:
    """Set the base git config for the detected platform.

    This function clones the repo with the recommended configs to a temporary
    directory, and sets the recommended base gitconfig. It also returns the
    recommended .gitattributes.

    Args:
        pl: A Platform object with the detected platform.
        test: True if testing

    Returns:
        The recommended .gitattributes
    """
    temp_dir = Path.home() / "temp-ssb-gitconfig"
    config_dir = temp_dir / "kvakk-git-tools" / "kvakk_git_tools" / "recommended"
    dst = Path().home() / ".gitconfig"
    src = config_dir / f"gitconfig-{pl.name().value}"
    if test:
        src = config_dir / "gitconfig-dapla"

    options = ["--branch", "2.2.3"]
    prod_zone_windows = pl.name() is PlatformName.PROD_WINDOWS_CITRIX
    prod_zone_linux = pl.name() is PlatformName.PROD_LINUX
    if prod_zone_windows or prod_zone_linux:
        options = ["-c", "http.sslVerify=False"]

    cmd = (
        ["git"]
        + ["clone", "https://github.com/statisticsnorway/kvakk-git-tools.git"]
        + options
    )
    print("Get recommended gitconfigs by cloning repo...")

    # Fix for python < 3.7, using stdout.
    # Use capture_output=true instead of stdout when python >= 3.7
    with TempDir(temp_dir):
        subprocess.run(cmd, cwd=temp_dir, stderr=subprocess.DEVNULL, check=True)
        dst.write_bytes(src.read_bytes())

        # Replace template username with real username
        if pl.name() is PlatformName.PROD_WINDOWS_CITRIX:
            windows_username = getpass.getuser()
            replace_text_in_file("username", windows_username, dst)

        gitattributes_file = config_dir / "gitattributes"
        return gitattributes_file.read_text(encoding="utf-8").rstrip()


def set_name_email(name: str, email: str) -> None:
    command = ["git", "config", "--global", "user.name", name]
    subprocess.run(command, stdout=subprocess.PIPE, check=True)

    command = ["git", "config", "--global", "user.email", email]
    subprocess.run(command, stdout=subprocess.PIPE, check=True)


def main(test: bool) -> None:
    detected_platform = Platform()
    print("This script sets the recommended gitconfig for the detected platform.")
    print(f"Script version: {__version__}")
    print(f"Detected platform: {detected_platform}")
    if not test and detected_platform.is_unsupported():
        print("The detected platform is currently unsupported by this script. Abort.")
        sys.exit(1)

    name = email = None
    gitconfig_file = Path.home() / ".gitconfig"
    if backup_gitconfig(gitconfig_file):
        name, email = extract_name_email()

    if not (name and email):
        if test:
            name = "John Doe"
            email = "johndoe@example.com"
        else:
            name, email = request_name_email()
    print(f"The config will use the following name and email address: {name} <{email}>")

    gitattributes = set_base_config(detected_platform, test)
    set_name_email(name, email)
    print(f"A new {gitconfig_file} created successfully.")

    print(
        "\nMake sure your repos contain a .gitattributes file in the root directory "
        "with the following lines:"
    )
    print(gitattributes)


def check_python_version() -> None:
    if (
        sys.version_info.major == 3 and sys.version_info.minor < 6
    ) or sys.version_info.major < 3:
        print("This script requires python version >= 3.6")
        sys.exit(1)


def kvakk_git_tools_package_installed() -> bool:
    """Checks if the kvakk_git_tools package is installed on the system.

    Returns:
        bool: True if the package is installed, False otherwise.
    """
    try:
        pkg_resources.get_distribution("kvakk_git_tools")
        return True
    except pkg_resources.DistributionNotFound:
        return False


def enable_additional_package_arguments(
    parser: argparse.ArgumentParser, enable: bool
) -> None:
    """Enables packages specific arguments in the given ArgumentParser object.

    Args:
        parser (argparse.ArgumentParser): The ArgumentParser object.
        enable (bool): Indicates whether to enable the additional arguments.
    """
    if enable:
        parser.add_argument(
            "--validate",
            action="store_true",
            help="Validates SSB gitconfig for your current platform",
        )


def parse_optional_validation_argument(validate: bool):
    """Parses the optional validation argument and performs SSB Git configuration validation.

    Args:
        validate (bool): Indicates whether to perform the validation.
    """
    if validate:
        from kvakk_git_tools.validate_ssb_gitconfig import validate_git_config

        if validate_git_config():
            print("Git configuration follows SSB recommendations.")
            exit(0)
        else:
            print(
                "WARNING: Git configuration does not follow SSB recommendations."
                "\nThis can lead to sensitive information being pushed to Git."
                "\nYou can fix this by running: 'kvakk-git-tools' in your terminal."
            )
            exit(1)


def run() -> None:
    check_python_version()

    parser = argparse.ArgumentParser(description=sys.modules[__name__].__doc__)
    parser.add_argument(
        "--test", action="store_true", help="used when testing the script"
    )
    parser.add_argument(
        "--version", action="store_true", help="print he version number of the script"
    )
    package_installed = kvakk_git_tools_package_installed()
    enable_additional_package_arguments(parser, package_installed)

    args = parser.parse_args()

    if package_installed:
        parse_optional_validation_argument(args.validate)

    if args.version:
        print(f"ssb_gitconfig version: {__version__}")
    else:
        main(args.test)


if __name__ == "__main__":
    run()
