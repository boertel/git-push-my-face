#!/bin/bash

# TODO update the path to your local file
SCRIPT_PATH=~/Code/git-push-my-face/post-commit
GITROOT="$(git rev-parse --show-toplevel)"

ln -s $SCRIPT_PATH $GITROOT/.git/hooks/post-commit

