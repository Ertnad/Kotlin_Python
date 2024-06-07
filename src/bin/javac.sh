#!/bin/bash

CD=$(dirname "$(readlink -f "$0")")  # "


JAVAC=/usr/bin/javac

[[ -e "$CD/_props.sh" ]] && . "$CD/_props.sh"


$JAVAC "$@"
