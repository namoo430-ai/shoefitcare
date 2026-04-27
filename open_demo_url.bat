@echo off
setlocal

set "DEMO_URL=https://shoefitcare.onrender.com/demo"

echo Opening demo URL...
echo %DEMO_URL%
start "" "%DEMO_URL%"

echo.
echo If browser does not open automatically, copy this URL:
echo %DEMO_URL%
echo.
pause

