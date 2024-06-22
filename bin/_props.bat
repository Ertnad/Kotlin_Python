@echo off

set PYTHON_HOME=C:\Users\Work\AppData\Local\Microsoft\WindowsApps
set PYTHON="%PYTHON_HOME%\python.exe"

set NET_HOME=C:\Windows\Microsoft.NET\Framework64\v4.0.30319

set CSC="%NET_HOME%\csc.exe"
set ILASM="%NET_HOME%\ilasm.exe"
set ILDASM="%~dp0.\.net\x86\ildasm.exe"
