#!/usr/bin/env python3
""" This script sets the recommended .gitconfig for the detected platform.

The recommended base git configs are stored in the public git repository
https://github.com/statisticsnorway/kvakk-git-tools.git. The script clones this
repo and selects the base git config based on the detected platform.

If there is an existing .gitconfig file, it is backed up, and the name and email
address are extracted from it and reused.
"""
import argparse
import getpass
import os
import platform
import shutil
import stat
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Tuple


def ping(host: str) -> bool:
    """Returns True if host responds to a ping request."""
    # Option for the number of packets is different on Windows and Linux
    ping_param = "-n" if platform.system() == "Windows" else "-c"

    # Timeout is -w <milliseconds> on Windows, and -W <seconds> on Linux
    timeout_param = "-w" if platform.system() == "Windows" else "-W"
    timeout_value = "1000" if platform.system() == "Windows" else "1"

    # Building the command. Ex: "ping -c 1 google.com"
    command = ["ping", ping_param, "1", timeout_param, timeout_value, host]

    # Fix for python < 3.7, using stdout.
    # Use capture_output=true instead of stdout when python >= 3.7
    return subprocess.run(command, stdout=subprocess.PIPE).returncode == 0


def remove_readonly(func, path, exc_info):
    """Workaround for a bug on Windows https://github.com/python/cpython/issues/87823

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
        if my_os == "Windows":
            self.windows = True
        if my_os == "Darwin":
            self.mac = True

        if os.environ.get("LOCAL_USER_PATH") is not None:
            self.dapla = True

        if not self.dapla:
            self.prod_zone = True if ping("sl-jupyter-p.ssb.no") else False
            if not self.prod_zone:
                self.adm_zone = True if ping("aw-dc04.ssb.no") else False
            session_name = os.environ.get("SESSIONNAME")
            self.citrix = (
                True if session_name is not None and "ICA" in session_name else False
            )

    def __repr__(self):
        return (
            f"{self.__class__.__qualname__}(linux={self.linux}, "
            f"windows={self.windows}, mac={self.mac}, dapla={self.dapla}, "
            f"adm_zone={self.adm_zone}, prod_zone={self.prod_zone}, "
            f"citrix={self.citrix})"
        )


class TempDir:
    """Context manager class for creating and cleaning up a temporary directory."""

    def __init__(self, temp_dir: Path):
        if temp_dir.exists():
            print(f"The directory {temp_dir} already exist.")
            assert temp_dir.exists() is False
        self.temp_dir = temp_dir

    def __enter__(self):
        self.temp_dir.mkdir(parents=True)
        return None

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


def get_gitconfig_element(element: str) -> str:
    cmd = ["git", "config", "--get", element]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, encoding="utf-8")
    return None if result.stdout == "" else result.stdout.strip()


def extract_name_email() -> Tuple[str, str]:
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
    else:
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

    with TempDir(temp_dir):
        options = []
        prod_zone_windows = pl.prod_zone and pl.windows and pl.citrix
        prod_zone_linux = pl.prod_zone and pl.linux
        if prod_zone_windows or prod_zone_linux:
            options = ["-c", "http.sslVerify=False"]

        cmd = (
            ["git"]
            + options
            + ["clone", "https://github.com/statisticsnorway/kvakk-git-tools.git"]
        )
        print("Get recommended gitconfigs by cloning repo...")

        # Fix for python < 3.7, using stdout.
        # Use capture_output=true instead of stdout when python >= 3.7
        subprocess.run(cmd, cwd=temp_dir, stdout=subprocess.PIPE)

        config_dir = temp_dir / "kvakk-git-tools" / "recommended"
        dst = Path().home() / ".gitconfig"

        if pl.prod_zone and pl.linux:
            src = config_dir / "gitconfig-prod-linux"
        elif pl.prod_zone and pl.windows and pl.citrix:
            src = config_dir / "gitconfig-prod-windows-citrix"
        elif pl.dapla:
            src = config_dir / "gitconfig-dapla"
        elif pl.adm_zone and pl.windows:  # just for testing on local pc
            src = config_dir / "gitconfig-prod-windows-citrix"
        elif pl.adm_zone and pl.mac:  # just for testing on local mac
            src = config_dir / "gitconfig-adm-mac"
        elif not test:
            print("The detected platform is currently unsupported. Aborting script.")
            sys.exit(1)
        else:
            src = config_dir / "gitconfig-prod-linux"  # use this when testing
        dst.write_bytes(src.read_bytes())

        # Replace template username with real username
        if pl.prod_zone and pl.windows and pl.citrix:
            windows_username = getpass.getuser()
            replace_text_in_file("username", windows_username, dst)

        gitattributes_file = config_dir / "gitattributes"
        return gitattributes_file.read_text(encoding="utf-8").rstrip()


def set_name_email(name: str, email: str) -> None:
    command = ["git", "config", "--global", "user.name", name]
    subprocess.run(command, stdout=subprocess.PIPE)

    command = ["git", "config", "--global", "user.email", email]
    subprocess.run(command, stdout=subprocess.PIPE)


def main(test: bool) -> None:
    detected_platform = Platform()
    print("This script sets the recommended gitconfig for the detected platform.")
    print(f"Detected platform: {detected_platform}")

    name = email = None
    gitconfig_file = Path.home() / ".gitconfig"
    if backup_gitconfig(gitconfig_file):
        name, email = extract_name_email()

    if not (name and email):
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=sys.modules[__name__].__doc__)
    parser.add_argument(
        "--test", action="store_true", help="used when testing the script"
    )
    args = parser.parse_args()

    main(args.test)
