@echo off
setlocal
rem mixmaster-local launcher (Windows). ASCII only on purpose: cmd.exe misreads UTF-8 batch files.
cd /d "%~dp0"
title mixmaster-local

rem An old .venv made with an unsupported Python (e.g. 3.14/3.15) is rebuilt automatically.
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" -c "import sys; sys.exit(0 if (3, 10) <= sys.version_info[:2] <= (3, 13) else 1)" >nul 2>&1 && goto deps
  echo Removing old .venv made with an unsupported Python version...
  rmdir /s /q .venv
)

echo Looking for Python 3.12 / 3.13 / 3.11 / 3.10 ...
set "PYCMD="
for %%V in (3.12 3.13 3.11 3.10) do (
  if not defined PYCMD (
    py -%%V -c "import sys" >nul 2>&1 && set "PYCMD=py -%%V"
  )
)
if not defined PYCMD (
  python -c "import sys; sys.exit(0 if (3, 10) <= sys.version_info[:2] <= (3, 13) else 1)" >nul 2>&1 && set "PYCMD=python"
)
if not defined PYCMD goto nopython

echo Using: %PYCMD%
%PYCMD% --version
echo Creating virtual environment (.venv)...
%PYCMD% -m venv .venv
if errorlevel 1 goto venvfail
if not exist ".venv\Scripts\python.exe" goto venvfail

:deps
set "STAMPFILE=.venv\installed.txt"
for %%F in (requirements.txt) do set "REQSTAMP=%%~zF %%~tF"
set "OLDSTAMP="
if exist "%STAMPFILE%" set /p OLDSTAMP=<"%STAMPFILE%"
if "%OLDSTAMP%"=="%REQSTAMP%" goto run

echo.
echo Installing dependencies. First time only, takes a few minutes, needs internet...
echo.
".venv\Scripts\python.exe" -m pip install --upgrade pip
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto pipfail
>"%STAMPFILE%" echo %REQSTAMP%

:run
echo.
echo ============================================================
echo  mixmaster-local is starting. The browser opens by itself.
echo  If not, open:  http://127.0.0.1:7860
echo  KEEP THIS WINDOW OPEN while you work. Close it to stop.
echo ============================================================
echo.
".venv\Scripts\python.exe" app.py
if errorlevel 1 (
  echo.
  echo ERROR: the app stopped with an error. See the messages above.
  echo Take a screenshot of this window and send it to Claude.
)
goto end

:nopython
echo.
echo ERROR: no suitable Python found. Needed: Python 3.12 (or 3.10 / 3.11 / 3.13).
echo Python 3.14 and newer are too new: some packages have no ready builds yet.
echo Installed Pythons on this PC:
py -0 2>nul
python --version 2>nul
echo.
echo Install Python 3.12 from https://www.python.org/downloads/windows/
echo (scroll to "Python 3.12.x", take "Windows installer (64-bit)").
echo Your other Python can stay installed. Then run this file again.
goto end

:venvfail
echo.
echo ERROR: could not create the .venv folder. See the messages above.
echo Try: delete the .venv folder (if it exists) and run again.
goto end

:pipfail
echo.
echo ERROR: installing dependencies failed. See the messages above.
echo Check the internet connection and run again.
echo If it says "Microsoft Visual C++ is required", your Python is too new: install Python 3.12.
echo If it still fails, take a screenshot and send it to Claude.
goto end

:end
echo.
echo Press any key to close this window...
pause >nul
