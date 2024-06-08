#!/bin/bash

CD=$(dirname "$(readlink -f "$0")")  # "


PYTHON_HOME=/opt/python3
PYTHON="$PYTHON_HOME/bin/python"

WINEPREFIX='$HOME/.wine.app'

WINE="eval WINEPREFIX=$WINEPREFIX wine"

CSC="$WINE 'c:/windows/Microsoft.NET/Framework/v2.0.50727/csc.exe'"
ILASM="$WINE 'c:/windows/Microsoft.NET/Framework/v2.0.50727/ilasm.exe'"
ILDASM="$WINE '"$CD"/.net/mono/ildasm.exe'"

CSC=mcs
ILASM=ilasm

JAVA=/usr/bin/java
JAVAC=/usr/bin/javac
JAR=/usr/bin/jar

PROGUARD="$CD/.java/proguard-assembler/bin/assembler.sh"
