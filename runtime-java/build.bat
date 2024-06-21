@echo off

%~d0
cd "%~dp0"


del /f /q .\CompilerDemo\*.class
call ..\bin\javac .\CompilerDemo\*.java
:: почему-то не работает с пакетами
::call ..\bin\proguard .\CompilerDemo\Runtime.class .\CompilerDemo\Runtime.jbc
