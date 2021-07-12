@echo off
echo Run Flask Server
start "" cmd /k call bat_Flask.bat
echo Run ngrok
start "" cmd /k call bat_ngrok.bat
echo over