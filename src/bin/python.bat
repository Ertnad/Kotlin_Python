@echo off

set PYTHON_HOME=C:\Program_Files\Python3
set PYTHON="%PYTHON_HOME%\bin\PYTHON3"

if exist "%~dp0.\_props.bat" call "%~dp0.\_props.bat"

%PYTHON% %*
