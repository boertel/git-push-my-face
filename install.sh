#!/bin/bash


sudo pip install twython

mkdir ~/.gitshots/

if [ "$(uname)" == "Darwin" ]; then
    brew install imagesnap
fi
