@echo off

set RUNTIME_MSIL=%~dp0.\runtime-net\runtime.msil

set PYTHON=python

if exist "%~dp0.\bin\_props.bat" call "%~dp0.\bin\_props.bat"
if exist "%~dp0.\_props.bat" call "%~dp0.\_props.bat"


if "%~1"=="" (
  (
    echo Usage:
    echo   %~nx0 src
  ) 1>&2
  exit 1
)
if not exist "%~1" (
  (
    echo File "%~1" not exists
  ) 1>&2
  exit 2
)


del /f /q "%~dpn1.exe" "%~dpn1.msil"
"%PYTHON%" "%~dp0\main.py" --msil-only "%~dpnx1" >"%~dpn1.msil"
set STATUS=%ERRORLEVEL%
if not "%STATUS%"=="0" (
  del /f /q "%~dpn1.msil"
  exit %STATUS%
)
"%~dp0.\bin\ilasm" /out:"%~dpn1.exe" "%~dpn1.msil" "%RUNTIME_MSIL%"
:: del /f /q "%~dpn1.msil"
