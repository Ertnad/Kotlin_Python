@echo off

set JAVA=java
set PROGUARD="%JAVA%" -jar "%~dp0\.java\proguard-assembler\lib\assembler.jar"

if exist "%~dp0.\_props.bat" call "%~dp0.\_props.bat"

%PROGUARD% %*
