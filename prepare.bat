@REM Ensure that the virtual environment does not exist.
del /s /q venv
rd /s /q venv
@REM Creat a virtual environment and install libraries.
python -m venv venv
.\venv\Scripts\pip install -r requirements.txt
ECHO [Success] Environment configuration completed.