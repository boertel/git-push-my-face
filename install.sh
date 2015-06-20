#!/bin/bash


if ! python -c "import twython"; then
    sudo pip install twython
fi

GITSHOTS_DIR="$HOME/.gitshots"
if [ ! -d "$GITSHOTS_DIR" ]; then
    echo "> creating $GITSHOTS_DIR"
    mkdir -p $GITSHOTS_DIR
fi

if [ "$(uname)" == "Darwin" ]; then
    if ! type "imagesnap" > /dev/null; then
        echo "> installing imagesnap"
        brew install imagesnap
    fi
fi

GIT_TEMPLATES_DIR="$HOME/.git-templates/"
if [ ! -d "$GIT_TEMPLATES_DIR" ]; then
    echo "> creating $GIT_TEMPLATES_DIR directory"
    HOOKS=$GIT_TEMPLATES_DIR/hooks/
    mkdir -p $HOOKS
    ln -s $PWD/post-commit $HOOKS
fi
git config --global init.templatedir $GIT_TEMPLATES_DIR
