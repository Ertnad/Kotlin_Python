@echo off

set JAR=jar

if exist "%~dp0.\_props.bat" call "%~dp0.\_props.bat"

%JAR% %*
