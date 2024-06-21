#!/bin/bash

cd "$(dirname "$(readlink -f "$0")")"  # "


rm -f ./runtime.netmodule ./runtime.msil
../bin/csc /target:module /out:./runtime.netmodule ./runtime.cs
chmod 'u-x,g-x,o-x' ./runtime.netmodule
../bin/ildasm /out:./runtime.msil ./runtime.netmodule
fromdos ./runtime.msil
