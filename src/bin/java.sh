#!/bin/bash

CD=$(dirname "$(readlink -f "$0")")  # "


JAVA=/usr/bin/java

[[ -e "$CD/_props.sh" ]] && . "$CD/_props.sh"


$JAVA "$@"
