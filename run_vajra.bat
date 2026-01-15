@echo off
:: Change to the project directory explicitly so this file can be run from anywhere (e.g. Desktop)
cd /d "f:\projects\processor"
call venv\Scripts\activate
python vajra.py
pause
