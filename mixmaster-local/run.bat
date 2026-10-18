@echo off
rem mixmaster-local launcher (Windows): creates .venv on first run, installs deps, starts the UI.
chcp 65001 >nul
cd /d "%~dp0"

if exist .venv\Scripts\python.exe goto deps
echo Creating .venv ...
for %%V in (3.12 3.11 3.10) do (
  py -%%V -c "import sys" >nul 2>&1 && ( py -%%V -m venv .venv & goto deps )
)
python -c "import sys; sys.exit(0 if (3,10)<=sys.version_info[:2]<=(3,12) else 1)" >nul 2>&1 && ( python -m venv .venv & goto deps )
echo Нужен Python 3.10-3.12 (Matchering не работает на 3.13+). Скачай Python 3.12 с python.org, при установке отметь "Add to PATH".
pause
exit /b 1

:deps
set "HASHFILE=.venv\.installed"
for %%F in (requirements.txt) do set "REQSTAMP=%%~zF_%%~tF"
set "OLDSTAMP="
if exist "%HASHFILE%" set /p OLDSTAMP=<"%HASHFILE%"
if "%OLDSTAMP%"=="%REQSTAMP%" goto run
echo Installing dependencies (one time, needs internet)...
.venv\Scripts\python -m pip install --upgrade pip
.venv\Scripts\python -m pip install -r requirements.txt || ( echo Ошибка установки зависимостей. & pause & exit /b 1 )
> "%HASHFILE%" echo %REQSTAMP%

:run
echo Starting UI: http://127.0.0.1:7860  (close this window to stop)
.venv\Scripts\python app.py
pause
