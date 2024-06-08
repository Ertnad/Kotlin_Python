#!/bin/bash

CD=$(dirname "$(readlink -f "$0")")  # "


WINEPREFIX='$HOME/.wine'

WINE="eval WINEPREFIX=$WINEPREFIX wine"

CSC="$WINE 'c:/windows/Microsoft.NET/Framework/v2.0.50727/csc.exe'"
ILASM="$WINE 'c:/windows/Microsoft.NET/Framework/v2.0.50727/ilasm.exe'"
ILDASM="$WINE '"$CD"/.net/mono/ildasm.exe'"

[[ -e "$CD/_props.sh" ]] && . "$CD/_props.sh"


$CSC "$@"
