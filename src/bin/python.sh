#!/bin/bash

CD=$(dirname "$(readlink -f "$0")")  # "


PYTHON=python

[[ -e "$CD/_props.sh" ]] && . "$CD/_props.sh"


$PYTHON "$@"
