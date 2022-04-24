# kvakk-git-tools
Repo for sharing recommended git config and git scripts in Statistics Norway.

This repo should cover git config files for the production zone Linux
and Windows (Citrix and VDI), JupyterLab (Dapla and production zone),
the administrative zone and stand alone.

It will also contain Ansible scripts for configuring linux servers with the
correct git version, firewall rules and so on.

Initially it will contain a collection of git configurations for the different
environments. But the aim is to make a common script, setting the recommended
git config for all environments.

## Directories
There is one directory for each environment. In addtion there is one directory
for the recommended `.gitattributes` file and one directory for the recommended
`.gitignore`-file.

The `ssb-gitconfig` directory is the root directory for the script that should
set the ssb recommended git config based on the detected environment. It is a
work in progress and not finished yet.

## Why not public repo
This repo is not public because it will contain Ansible scripts with
information about production zone server configurations and server names.