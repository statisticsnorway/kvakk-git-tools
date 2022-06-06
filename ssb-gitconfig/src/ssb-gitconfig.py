#!/usr/bin/env python3

import os
import platform
import shutil
import stat
import subprocess
from datetime import datetime
from pathlib import Path


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
    def __init__(self):
        my_os = platform.system()
        self.linux = True if my_os == "Linux" else False
        self.windows = True if my_os == "Windows" else False

        local_user_path = os.environ.get("LOCAL_USER_PATH")
        self.dapla = True if local_user_path is not None else False

        self.prod_zone = True if ping("jupyter-prod.ssb.no") else False

        self.adm_zone = False
        if not self.prod_zone and not self.dapla:
            self.adm_zone = True if ping("aw-dc04.ssb.no") else False

        session_name = os.environ.get("SESSIONNAME")
        self.citrix = (
            True if session_name is not None and "ICA" in session_name else False
        )

    def __repr__(self):
        return (
            f"{self.__class__.__qualname__}(linux={self.linux}, "
            f"windows={self.windows}, dapla={self.dapla}, "
            f"adm_zone={self.adm_zone}, prod_zone={self.prod_zone}, "
            f"citrix={self.citrix})"
        )


class TempDir:
    def __init__(self, temp_dir: Path):
        if temp_dir.exists():
            print(f"The directory {temp_dir} already exist.")
            assert temp_dir.exists() is False
        self.temp_dir = temp_dir

    def __enter__(self):
        print("Enter TempDir")
        self.temp_dir.mkdir(parents=True)
        return None

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("Exit TempDir")
        if platform.system() == "Windows":
            # Workaround for bug https://github.com/python/cpython/issues/87823
            shutil.rmtree(self.temp_dir, onerror=remove_readonly)
        else:
            shutil.rmtree(self.temp_dir)


def extract_username_email(file: Path) -> tuple[str, str]:
    name = email = None
    content = file.read_text().splitlines()
    for line in content:
        words = line.split()
        if len(words) >= 3:
            if words[0] == "email":
                email = words[2]
            elif words[0] == "name":
                name = " ".join(words[2:]).strip('"')
    return name, email


def backup_gitconfig(gitconfig_file: Path) -> bool:
    if gitconfig_file.is_file():
        timestamp_str = datetime.now().strftime("%y%m%d_%H%M%S")
        destination_filename = f".gitconfig_{timestamp_str}"
        print(f"Backup .gitconfig to {destination_filename}")

        backup_file = Path.home() / destination_filename
        # backup_file.write_bytes(gitconfig_file.read_bytes())
        print(f"Backup created: {backup_file}")
        return True
    else:
        return False


def request_username_email() -> tuple[str, str]:
    print("Git needs to know your name (first name and surname) and email address.")
    name = input("Enter name: ")
    email = input("Enter email: ")
    return name, email


def set_base_config(pl: Platform) -> None:
    root_dir = Path.home() / "temp"

    with TempDir(root_dir):
        cmd = ["git", "clone", "https://github.com/statisticsnorway/kvakk-git-tools.git"]

        # Fix for python < 3.7, using stdout.
        # Use capture_output=true instead of stdout when python >= 3.7
        subprocess.run(cmd, cwd=root_dir, stdout=subprocess.PIPE)

        dst = Path().home() / ".gitconfig_new"
        if pl.windows and pl.adm_zone:
            src = root_dir / "kvakk-git-tools" / "recommended" / "gitconfig-prod-windows-citrix"
            dst.write_bytes(src.read_bytes())


def main():
    pl = Platform()
    print(pl)

    name = email = None
    gitconfig_file = Path.home() / ".gitconfig"
    if backup_gitconfig(gitconfig_file):
        name, email = extract_username_email(gitconfig_file)

    if not (name and email):
        name, email = request_username_email()
    print(f"{name} <{email}>")

    set_base_config(pl)


if __name__ == "__main__":
    main()
