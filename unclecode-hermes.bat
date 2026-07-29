@echo off
setlocal
set "ROOT=%~dp0"
set "PYTHONPATH="
set "VIRTUAL_ENV=%ROOT%.venv"
set "PATH=%ROOT%.venv\Scripts;%PATH%"
"%ROOT%.venv\Scripts\unclecode-hermes.exe" %*
endlocal
