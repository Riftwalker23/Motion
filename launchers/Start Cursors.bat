@echo off
rem Starts the multi-cursor overlay. F9 = hide/show, F10 = quit.
rem Uses the installed skill if present, otherwise the copy in this repo.
rem Extra args pass through, e.g.:  "Start Cursors.bat" --preset screen --labels "Data,Formulas,QA"
set "CTL=%USERPROFILE%\.claude\skills\multi-cursor\scripts\cursorctl.py"
if not exist "%CTL%" set "CTL=%~dp0..\skills\multi-cursor\scripts\cursorctl.py"
if "%~1"=="" (python "%CTL%" start --preset proteus) else (python "%CTL%" start %*)
