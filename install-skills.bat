@echo off
rem Copies the skills in this repo into your personal Claude Code skills folder.
set "DEST=%USERPROFILE%\.claude\skills"
if not exist "%DEST%" mkdir "%DEST%"
xcopy /E /I /Y "%~dp0skills\pc-control" "%DEST%\pc-control" >nul
xcopy /E /I /Y "%~dp0skills\multi-cursor" "%DEST%\multi-cursor" >nul
echo Installed pc-control and multi-cursor to %DEST%
pause
