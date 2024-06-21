@echo off

set RUNTIME_JAVA=%~dp0.\runtime-java

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


del /f /q "%~dpn1.jbc" "%~dpn1.class" "%~dpn1.jar" >NUL 2>&1
call "%~dp0.\bin\python" -Xutf8 "%~dp0\main.py" --jbc-only "%~dpnx1" >"%~dpn1.jbc"
set STATUS=%ERRORLEVEL%
if not "%STATUS%"=="0" (
  del /f /q "%~dpn1.jbc"
  exit %STATUS%
)
for /f "tokens=3" %%V in ('type "%~dpn1.jbc" ^| findstr /b "public class"') do set CLASS_NAME=%%V
move "%~dpn1.jbc" "%~dp1.\%CLASS_NAME%.jbc" >NUL 2>&1
call "%~dp0.\bin\proguard" "%~dp1.\%CLASS_NAME%.jbc" "%~dp1.\%CLASS_NAME%.class"
call "%~dp0.\bin\jar" --create --file "%~dpn1.jar" --main-class "%CLASS_NAME%" -C "%~dp1." "%CLASS_NAME%.class" -C "%RUNTIME_JAVA%" CompilerDemo/Runtime.class
:: del /f /q "%~dp1.\%CLASS_NAME%.jbc" "%~dp1.\%CLASS_NAME%.class"
