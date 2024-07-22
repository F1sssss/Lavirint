@ECHO OFF

@REM Postavlja UTF-8 Code Page
chcp 65001 >NUL

if "%1" == "" goto :help
if "%1" == "help" goto :help
if "%1" == "run-background" goto :run-background
if "%1" == "run" goto :run
if "%1" == "stop" goto :stop
if "%1" == "test" goto :test
if "%1" == "freeze" goto :freeze
if "%1" == "freeze-test" goto :freeze-test
if "%1" == "pack" goto :pack
echo Greška: Komanda "%1" ne postoji.
echo.
goto :help

@REM -------------------------------------------------------------------------------------------------------------------

:help
echo Moguće komande su:
echo run-background   Runs the server as background process
echo run              Runs the server (blocking)
echo stop             Isključuje aplikaciju ako je pokrenuta
echo test             Run quality control and tests
echo freeze           Pin all requirements including sub dependencies into requirements.txt
echo freeze-test      Pin all requirements for test including sub dependencies into requirements_for_test.txt
echo pack             Copies all the files for migration
goto :end

:run
call environment.bat
python run.py
goto :end

:run-background
call environment.bat
python kill.py -y
start /B python run.py
goto :end

:test
call environment.bat
flake8 .
isort --check-only .
pytest -n4 --maxfail=10
goto :end

:freeze
call environment.bat ^
&& pip install --upgrade pip-tools ^
&& pip-compile --generate-hashes requirements.in
goto :end

:freeze-test
call environment.bat ^
&& pip install --upgrade pip-tools ^
&& pip-compile --generate-hashes --output-file=requirements_for_test.txt requirements_for_test.in
goto :end

:pack
call environment.bat ^
echo "Test"
robocopy /e .\backend .\pack\backend
robocopy /e .\backend .\pack\backend
robocopy /e .\fonts .\pack\fonts
robocopy /e .\migrations .\pack\migrations
robocopy /e .\schemas .\pack\schemas
robocopy /e .\scripts .\pack\scripts
robocopy /e .\test_files .\pack\test_files
robocopy /e .\tests .\pack\tests
robocopy .\ .\pack alembic.ini
robocopy .\ .\pack CHANGELOG.md
robocopy .\ .\pack kill.py
robocopy .\ .\pack make.bat
robocopy .\ .\pack Makefile
robocopy .\ .\pack README.md
robocopy .\ .\pack requirements.in
robocopy .\ .\pack requirements.txt
robocopy .\ .\pack requirements_for_test.in
robocopy .\ .\pack requirements_for_test.txt
robocopy .\ .\pack run.py
robocopy .\ .\pack setup.cfg
for /d /r pack %d in (__pycache__) do @if exist "%d" rd /s/q "%d"
goto :end

:stop
call environment.bat
python kill.py -y
goto :end

:end
