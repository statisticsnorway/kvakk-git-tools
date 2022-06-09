# kvakk-git-tools
Repo for sharing recommended git config and git scripts in Statistics Norway.

This repo should cover git config files for the production zone, Linux
and Windows (Citrix and VDI), JupyterLab (Dapla and production zone),
administrative zone and stand alone.

Initially the repo will contain a collection of git configurations for the different
environments. But the aim is to make a common script, setting up the recommended
git config, based on the detected environment.

## Directories
The `existing` directory contains configurations collected from existing environments
before any recommendations are implemented. The `recommended` directory contains the
recommended config files for the different environments.

The `ssb-gitconfig` directory is the root directory for the script that should
set the ssb recommended git config based on the detected environment. It is a
work in progress and not finished yet.

## Usage
Linux:
```shell
git clone https://github.com/statisticsnorway/kvakk-git-tools.git
kvakk-git-tools/ssb-gitconfig/src/ssb-gitconfig.py
```

Windows:
```shell
git clone https://github.com/statisticsnorway/kvakk-git-tools.git
python kvakk-git-tools\ssb-gitconfig\src\ssb-gitconfig.py
```
