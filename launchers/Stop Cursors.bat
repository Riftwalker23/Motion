@echo off
set "CTL=%USERPROFILE%\.claude\skills\multi-cursor\scripts\cursorctl.py"
if not exist "%CTL%" set "CTL=%~dp0..\skills\multi-cursor\scripts\cursorctl.py"
python "%CTL%" stop
