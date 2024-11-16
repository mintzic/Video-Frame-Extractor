@echo off
echo Activating virtual environment...
call .venv\Scripts\activate

echo Installing/Updating requirements...
pip install -r requirements.txt

echo Building executable...
python build.py

echo Done! Executable is in the dist folder.
pause