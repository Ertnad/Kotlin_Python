#!/bin/bash

cd "$(dirname "$(readlink -f "$0")")"  # "


rm -f ./CompilerDemo/*.class
../bin/javac ./CompilerDemo/*.java
# почему-то не работает с пакетами
#call ../bin/proguard ./CompilerDemo/Runtime.class ./CompilerDemo/Runtime.jbc
