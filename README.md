# kvakk-git-tools
Repo for sharing recommended git config and git scripts in Statistics Norway.

This repo should cover git config files should cover the production zone, Linux
and Windows (Citrix and VDI), JupyterLab (Dapla and production zone),
administrative zone and stand alone.

It will also contain Ansible scripts for configuring linux servers with the
correct git version, firewall rules and so on.

Initially it will contain a collection of git configurations for the different
environments. But the aim is to make a common script, setting the recommended
git config for all environments.

## Directories
The `existing` directory contains configurations collected from existing environments
before any recommendations are implemented. The `recommended` directory contains the
recommended config files for the different environments.

## Why not public repo
This repo is not public because it will contain Ansible scripts with
information about production zone server configurations and server names.