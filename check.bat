
@echo off
chcp 65001 > nul
setlocal

echo.
echo ========================================
echo   DARK FANTASY AI GM - PROJECT CHECK
echo ========================================
echo.

echo [1/3] Проверка Git diff...
git diff --check
if errorlevel 1 goto error

echo.
echo [2/3] Проверка Backend...
pushd "%~dp0backend"
python -m unittest discover -s tests -v
if errorlevel 1 goto error
popd

echo.
echo [3/3] Сборка Frontend...
pushd "%~dp0frontend"
call npm run build
if errorlevel 1 goto error
popd

echo.
echo ========================================
echo   ALL CHECKS PASSED!
echo ========================================
pause
exit /b 0

:error
echo.
echo ========================================
echo   CHECK FAILED!
echo   See the error above.
echo ========================================
pause
exit /b 1
