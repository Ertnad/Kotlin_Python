@echo off

%~d0
cd "%~dp0"


del /f /q .\runtime.netmodule .\runtime.msil
call ..\bin\csc /target:module /out:.\runtime.netmodule .\runtime.cs
call ..\bin\ildasm /text /out:.\runtime.msil .\runtime.netmodule
