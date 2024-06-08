#!/bin/bash

CD=$(dirname "$(readlink -f "$0")")  # "


JAR=/usr/bin/jar

[[ -e "$CD/_props.sh" ]] && . "$CD/_props.sh"


$JAR "$@"
