@echo off

set PYTHON=X:\Python\Python34


setlocal EnableDelayedExpansion
set PARAMS=
for %%P in (%*) do (
  if exist "%%~P" (
    set PARAMS=!PARAMS! "%%~fP"
  ) else (
    set PARAMS=!PARAMS! "%%~P"
  )
)
setlocal DisableDelayedExpansion


"%PYTHON%\python.exe" main.py %PARAMS%
