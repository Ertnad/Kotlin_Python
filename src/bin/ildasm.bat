@echo off

set NET_HOME=C:\Windows\Microsoft.NET\Framework64\v4.0.30319

set CSC=csc.exe
set ILASM=ilasm.exe
set ILDASM=ildasm.exe

if exist "%~dp0.\_props.bat" call "%~dp0.\_props.bat"

%ILDASM% %*
