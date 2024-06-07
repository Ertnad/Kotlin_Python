@echo off

REM Подключение _props.bat
if exist ..\..\_props.bat call ..\..\_props.bat
if exist ..\_props.bat call ..\_props.bat
if exist .\_props.bat call .\_props.bat

REM Настройка путей для Anaconda (если необходимо)
if exist "%CD%\Anaconda3" (
  set CONDA_PATH=%CD%\Anaconda3
) else (
  set CONDA_PATH=X:\Python\Anaconda3
)

REM Установка QT_QPA_PLATFORM_PLUGIN_PATH
if "%QT_QPA_PLATFORM_PLUGIN_PATH%"=="" (
  set QT_QPA_PLATFORM_PLUGIN_PATH=%CONDA_PATH%\Library\plugins
)

REM Добавление путей к Graphviz
set ADD_PATH=
if exist "%CONDA_PATH%\Library\opt\graphviz-64" (
  set ADD_PATH=%CONDA_PATH%\Library\opt\graphviz-64;%ADD_PATH%
)
if exist "%CONDA_PATH%\Library\opt\graphviz" (
  set ADD_PATH=%CONDA_PATH%\Library\opt\graphviz;%ADD_PATH%
)

REM Установка переменных Oracle (если необходимо)
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
set NLS_LANG=RUSSIAN_CIS.UTF8
set PATH=%ADD_PATH%;%PATH%

REM Обработка параметров командной строки
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

REM Запуск main.py с параметрами
%PYTHON% "%~dp0\src\main.py" %PARAMS%
