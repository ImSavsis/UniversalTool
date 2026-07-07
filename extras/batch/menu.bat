@echo off
REM extras/batch/menu.bat -- decorative, not part of the real installer.
REM the real launcher is app/start.bat (just "python app.py"). this one is
REM just a slightly fancier menu wrapper, kept here for show.

setlocal enabledelayedexpansion
title nexdex.space -- dev menu

:menu
cls
echo ============================================
echo   nexdex.space -- dev menu
echo   made by savsis with ^<3
echo ============================================
echo.
echo   1. run the app  (python app.py)
echo   2. install dependencies  (pip install -r requirements.txt)
echo   3. format a python file with black
echo   4. open downloads folder
echo   5. exit
echo.
set /p choice="choose 1-5: "

if "%choice%"=="1" goto run
if "%choice%"=="2" goto deps
if "%choice%"=="3" goto format
if "%choice%"=="4" goto downloads
if "%choice%"=="5" goto end
goto menu

:run
cd /d "%~dp0..\..\app"
python app.py
pause
goto menu

:deps
cd /d "%~dp0..\..\app"
pip install -r requirements.txt
pause
goto menu

:format
set /p pyfile="path to .py file: "
python -m black "%pyfile%"
pause
goto menu

:downloads
start "" "%~dp0..\..\app\downloads"
goto menu

:end
endlocal
exit /b 0
