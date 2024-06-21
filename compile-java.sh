#!/bin/bash

CD=$(dirname "$(readlink -f "$0")")  # "

RUNTIME_JAVA="$CD/runtime-java"

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


rm -f "${FILENAME%.*}.jbc" "${FILENAME%.*}.class" "${FILENAME%.*}.jar"
JBC=$("$PYTHON" "$CD/main.py" --jbc-only "$FILENAME")
STATUS=$?
if [[ $STATUS -ne 0 ]]; then
  exit $STATUS
fi
CLASS_NAME=$(echo "$JBC" | grep 'public class' | sed 's/.*class \(\w\+\).*/\1/')  # '
DIR=$(dirname "$FILENAME")
rm -f "$DIR/$CLASS_NAME.jbc" "$DIR/$CLASS_NAME.class"
echo "$JBC" >"$DIR/$CLASS_NAME.jbc"
"$CD/bin/proguard" "$DIR/$CLASS_NAME.jbc" "$DIR/$CLASS_NAME.class"
"$CD/bin/jar" --create --file "${FILENAME%.*}.jar" --main-class "$CLASS_NAME" -C "$DIR" "$CLASS_NAME.class" -C "$RUNTIME_JAVA" CompilerDemo/Runtime.class
# rm -f "$DIR/$CLASS_NAME.jbc" "$DIR/$CLASS_NAME.class"
