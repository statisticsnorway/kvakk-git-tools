#!/usr/bin/env bash

# helper script for git-config.sh

checkGitConfig() {
  if [ -f $GIT_CONFIG ]; then
    CONFIG_EXISTS_MESSAGE="A Gitconfig already exists! "
  fi

  while ! [[ "$ASK_CREATE_NEW_GIT_CONFIG" =~ ^(y|Y|n|N)$ ]]; do
    echo -n "$CONFIG_EXISTS_MESSAGE""Do you want to create a new profile? [y/n]: "
    read -r ASK_CREATE_NEW_GIT_CONFIG

    if [ -z "$ASK_CREATE_NEW_GIT_CONFIG" ]; then
      ASK_CREATE_NEW_GIT_CONFIG="N"
    fi

    if [[ "$ASK_CREATE_NEW_GIT_CONFIG" =~ ^(y|Y)$ ]]; then
      configureGitConfig
    elif [[ "$ASK_CREATE_NEW_GIT_CONFIG" =~ ^(n|N)$ ]]; then
      continue
    fi
  done
}

configureGitConfig() {
  echo -n "Enter Full name: "
  read -r GIT_FULL_NAME

  echo -n "Enter Email: "
  read -r GIT_EMAIL

  echo -n "Enter Git Username: "
  read -r GIT_USERNAME

  cat >"$GIT_CONFIG" <<EOF
[user]
        name = $GIT_FULL_NAME
        email = $GIT_EMAIL
[credential]
        username = $GIT_USERNAME
        helper = cache --timeout=3600
[core]
        autocrlf = input
[diff "jupyternotebook"]
        command = git-nbdiffdriver diff
[merge "jupyternotebook"]
        driver = git-nbmergedriver merge %O %A %B %L %P
        name = jupyter notebook merge driver
[difftool "nbdime"]
        cmd = git-nbdifftool diff \"$LOCAL\" \"$REMOTE\" \"$BASE\"
[difftool]
        prompt = false
[mergetool "nbdime"]
        cmd = git-nbmergetool merge \"$BASE\" \"$LOCAL\" \"$REMOTE\" \"$MERGED\"
[mergetool]
        prompt = false
[filter "nbstripout"]
        clean = '/opt/conda/bin/python3' -m nbstripout
        smudge = cat
[diff "ipynb"]
        textconv = '/opt/conda/bin/python3' -m nbstripout -t
EOF
  chmod 600 "$GIT_CONFIG"
        cat <<EOF

Your git-config is successfully configured!

EOF
  GIT_CONFIG_SUCCESSFUL=true
}

createGitConfig() {
  checkGitConfig
}
