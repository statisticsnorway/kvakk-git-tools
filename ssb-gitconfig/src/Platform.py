import os
import platform
import subprocess


def ping(host: str) -> bool:
    """
    Returns True if host (str) responds to a ping request.
    """
    # Option for the number of packets is different on Windows and Linux
    ping_param = "-n" if platform.system() == "Windows" else "-c"

    # Timeout is -w <milliseconds> on Windows, and -W <seconds> on Linux
    timeout_param = "-w" if platform.system() == "Windows" else "-W 1"
    timeout_value = "1000" if platform.system() == "Windows" else "1"

    # Building the command. Ex: "ping -c 1 google.com"
    command = ["ping", ping_param, "1", timeout_param, timeout_value, host]
    return subprocess.run(command, capture_output=True).returncode == 0


class Platform:
    def __init__(self):
        my_os = platform.system()
        self.linux = True if my_os == "Linux" else False
        self.windows = True if my_os == "Windows" else False

        local_user_path = os.environ.get("LOCAL_USER_PATH")
        self.dapla = True if local_user_path is not None else False

        self.prod_zone = True if ping("jupyter-prod.ssb.no") else False

        # How to check for adm zone? Which server? Or which environment variable?
        self.adm_zone = True if ping("ssb.no") else False

        session_name = os.environ.get("SESSIONNAME")
        self.citrix = True if "ICA" in session_name else False

    def __repr__(self):
        return f"{self.__class__.__qualname__}(linux={self.linux}, " \
               f"windows={self.windows}, dapla={self.dapla}, " \
               f"adm_zone={self.adm_zone}, prod_zone={self.prod_zone}, " \
               f"citrix={self.citrix})"


def main():
    pl = Platform()
    print(pl)


if __name__ == "__main__":
    main()
