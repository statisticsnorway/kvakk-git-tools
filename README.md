# kvakk-git-tools

Repo for sharing recommended git config and git scripts in Statistics Norway.

This repo should cover git config files for the production zone, Linux
and Windows (Citrix and VDI), JupyterLab (Dapla and production zone),
administrative zone and stand alone.

Initially the repo will contain a collection of git configurations for the different
environments. But the aim is to make a common script, setting up the recommended
git config for all SSB platforms, based on the detected environment.

## Status

The `ssb_gitconfig.py` script works and is tested on the following platforms:

- Dapla
- Production zone, Linux (including Jupyter)
- Production zone, Windows (Citrix)

## Directories

The `existing` directory contains configurations collected from existing environments
before any recommendations are implemented. The `recommended` directory contains the
recommended config files for the different environments.

The `ssb_gitconfig` directory is the root directory for the script that should
set the ssb recommended git config based on the detected environment. It is a
work in progress and not finished yet.

## Usage

Linux and Mac OS:

```shell
git clone https://github.com/statisticsnorway/kvakk-git-tools.git
kvakk-git-tools/kvakk_git_tools/ssb_gitconfig.py
```

Windows:

```shell
git clone https://github.com/statisticsnorway/kvakk-git-tools.git
python kvakk-git-tools\kvakk_git_tools\ssb_gitconfig.py
```

## Developer guide

### Initial setup

The Poetry tool is used for dependency management. Install poetry as described on the
[Poetry installation page](https://python-poetry.org/docs/#installation), if not
already installed. Then run the following commands in the cloned repo:

```shell
poetry install
poetry run pre-commit install
```

### Source code requirements

- The source code must support python version 3.6, because one of the supported platforms
  is based on RHEL 7.
- It shall be possible to run the script from a plain python installation. That is:
  Don't use external libraries.
- The source code shall run on these platforms: Linux, Windows and macOS.

### Linting

You can do local linting with the following commands:

```shell
poetry run flake8
poetry run mypy .
poetry run pylint kvakk_git_tools/*.py
```

### Bumping version

Use `make` to bump the _patch_, _minor_ version or _major_ version before creating a pull request to the `main` GIT
branch.

You can use either `bump-version-patch`, `bump-version-minor`, or `bump-version-major`.
Bumping must be done with a clean git working space, and automatically commits with the new version number.

Then just run `git push origin --tags` to push the changes and trigger the release process.

### Building and releasing

Before merging your changes into the `main` branch, make sure you have bumped the version like outlined above.

An automatic release process will build _kvakk-git-tools_ and release a new version of the package to **pypi.org** automatically.
