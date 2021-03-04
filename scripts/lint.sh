#! /bin/sh

if [ "$1" = "--fix" ]; then
    # check flake8
    flake8

    # fix sorted imports
    isort haku

    # fix black formatting
    black haku

else
    # check flake8
    flake8

    # check sorted imports
    isort --check --diff --color haku

    # check black formatting
    black --check --diff --color haku
fi
