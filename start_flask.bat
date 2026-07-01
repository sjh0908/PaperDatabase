@echo off
set MYSQL_PASSWORD=123456
cd /d "C:\Users\s\Desktop\PaperDatabase"
"C:\Users\s\Desktop\PaperDatabase\.venv\Scripts\python.exe" "C:\Users\s\Desktop\PaperDatabase\app.py" > "C:\Users\s\Desktop\PaperDatabase\flask.log" 2>&1
