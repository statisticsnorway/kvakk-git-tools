# KVAKK Git Tools

[![PyPI](https://img.shields.io/pypi/v/kvakk-git-tools.svg)][pypi status]
[![Status](https://img.shields.io/pypi/status/kvakk-git-tools.svg)][pypi status]
[![Python Version](https://img.shields.io/pypi/pyversions/kvakk-git-tools)][pypi status]
[![License](https://img.shields.io/pypi/l/kvakk-git-tools)][license]

[![Documentation](https://github.com/statisticsnorway/kvakk-git-tools/actions/workflows/docs.yml/badge.svg)][documentation]
[![Tests](https://github.com/statisticsnorway/kvakk-git-tools/actions/workflows/tests.yml/badge.svg)][tests]
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=statisticsnorway_kvakk-git-tools&metric=coverage)][sonarcov]
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=statisticsnorway_kvakk-git-tools&metric=alert_status)][sonarquality]

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)][pre-commit]
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)][black]
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Poetry](https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json)][poetry]

[pypi status]: https://pypi.org/project/kvakk-git-tools/
[documentation]: https://statisticsnorway.github.io/kvakk-git-tools
[tests]: https://github.com/statisticsnorway/kvakk-git-tools/actions?workflow=Tests
[sonarcov]: https://sonarcloud.io/summary/overall?id=statisticsnorway_kvakk-git-tools
[sonarquality]: https://sonarcloud.io/summary/overall?id=statisticsnorway_kvakk-git-tools
[pre-commit]: https://github.com/pre-commit/pre-commit
[black]: https://github.com/psf/black
[poetry]: https://python-poetry.org/

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
poetry run ruff check .
```

### Bumping version

Just change the version number in `pyproject.toml` to the new version number.
Or use the command `poetry version` followed by `major`, `minor` or `patch`.

### Building and releasing

An automatic release process will build _kvakk-git-tools_ and release a new version of the package to either **pypi.org** or **test.pypi.org** automatically, when merging to the main branch.

If the version number is *not* changed, it is published to TestPyPI.
If the version number *is* changed, it is published to PyPI.


## Credits

This project was generated from [Statistics Norway]'s [SSB PyPI Template].

[statistics norway]: https://www.ssb.no/en
[pypi]: https://pypi.org/
[ssb pypi template]: https://github.com/statisticsnorway/ssb-pypitemplate
[file an issue]: https://github.com/statisticsnorway/kvakk-git-tools/issues
[pip]: https://pip.pypa.io/

<!-- github-only -->

[license]: https://github.com/statisticsnorway/kvakk-git-tools/blob/main/LICENSE
[contributor guide]: https://github.com/statisticsnorway/kvakk-git-tools/blob/main/CONTRIBUTING.md
[reference guide]: https://statisticsnorway.github.io/kvakk-git-tools/reference.html
