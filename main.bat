@echo off

if exist "%CD%\Anaconda3" (
  set CONDA_PATH=%CD%\Anaconda3
) else (
  set CONDA_PATH=X:\Python\Anaconda3
)


if exist ..\..\_props.bat call ..\..\_props.bat
if exist ..\_props.bat call ..\_props.bat
if exist .\_props.bat call .\_props.bat


if "%QT_QPA_PLATFORM_PLUGIN_PATH%"=="" (
  set QT_QPA_PLATFORM_PLUGIN_PATH=%CONDA_PATH%\Library\plugins
)

set ADD_PATH=
if exist "%CONDA_PATH%\Library\opt\graphviz-64" (
  set ADD_PATH=%CONDA_PATH%\Library\opt\graphviz-64;%ADD_PATH%
)
if exist "%CONDA_PATH%\Library\opt\graphviz" (
  set ADD_PATH=%CONDA_PATH%\Library\opt\graphviz;%ADD_PATH%
)
if "%TNS_ADMIN%"=="" (
  if not "%ORACLE_HOME%"=="" (
    set TNS_ADMIN=%ORACLE_HOME%\network\admin
  )
)
if exist "%CONDA_PATH%\Library\opt\instantclient" (
  set ORACLE_HOME=%CONDA_PATH%\Library\opt\instantclient
  set ADD_PATH=%CONDA_PATH%\Library\opt\instantclient;%ADD_PATH%
  if "%TNS_ADMIN%"=="" (
    set TNS_ADMIN=%ORACLE_HOME%\network\admin
  )
)
::set NLS_LANG=RUSSIAN_CIS.CL8MSWIN1251
set NLS_LANG=RUSSIAN_CIS.UTF8
set PATH=%ADD_PATH%;%PATH%


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


"%CONDA_PATH%\python.exe" main.py %PARAMS%
