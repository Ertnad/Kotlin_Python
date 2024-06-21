#!/bin/bash

CD=$(dirname "$(readlink -f "$0")")  # "

RUNTIME_MSIL="$CD/runtime-net/runtime.msil"

PYTHON=python

[[ -e "$CD/bin/_props.sh" ]] && . "$CD/bin/_props.sh"
[[ -e "$CD/_props.sh" ]] && . "$CD/_props.sh"


FILENAME="$1"
if [[ -z $FILENAME ]]; then
  (
    echo 'Usage:'
    echo "  $0 src"
  ) >/dev/stderr
  exit 1
fi
if [[ ! -e $FILENAME ]]; then
  (
    echo "File \"$FILEMAME\" not exists"
  ) >/dev/stderr
  exit 2
fi


rm -f "${FILENAME%.*}.exe" "${FILENAME%.*}.msil"
"$PYTHON" "$CD/main.py" --msil-only "$FILENAME" >"${FILENAME%.*}.msil"
STATUS=$?
if [[ $STATUS -ne 0 ]]; then
  rm -f "${FILENAME%.*}.msil"
  exit $STATUS
fi
"$CD/bin/ilasm" /out:"${FILENAME%.*}.exe" "${FILENAME%.*}.msil" "$RUNTIME_MSIL"
# rm -f "${FILENAME%.*}.msil"
chmod "u+x,g+x,o+x" "${FILENAME%.*}.exe"
