@echo off

set JAVAC=java

if exist "%~dp0.\_props.bat" call "%~dp0.\_props.bat"

%JAVA% %*
