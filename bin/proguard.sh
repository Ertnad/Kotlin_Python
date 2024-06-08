#!/bin/bash

CD=$(dirname "$(readlink -f "$0")")  # "


PROGUARD="$CD/.java/proguard-assembler/bin/assembler.sh"

[[ -e "$CD/_props.sh" ]] && . "$CD/_props.sh"


"$PROGUARD" "$@"
