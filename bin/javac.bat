@echo off

set JAVAC=javac

if exist "%~dp0.\_props.bat" call "%~dp0.\_props.bat"

%JAVAC% %*
