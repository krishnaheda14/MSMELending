@echo off
REM Quick test script for advanced features - Windows batch file
REM Usage: test_features.bat [CUSTOMER_ID]

setlocal enabledelayedexpansion

set CUSTOMER_ID=%1
if "%CUSTOMER_ID%"=="" set CUSTOMER_ID=CUST_MSM_00001

echo.
echo ================================================================
echo   MSME Lending - Advanced Features Quick Test
echo ================================================================
echo.
echo Customer ID: %CUSTOMER_ID%
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found in PATH
    echo Please install Python 3.11+ and add to PATH
    exit /b 1
)

echo [INFO] Checking analytics directory...
cd /d "%~dp0analytics"

REM Check if analytics files exist
if not exist "%CUSTOMER_ID%_overall_summary.json" (
    echo [WARN] Analytics files not found for %CUSTOMER_ID%
    echo.
    echo Generating analytics data...
    cd ..
    python generate_all.py --customer-id %CUSTOMER_ID%
    python pipeline/clean_data.py --customer-id %CUSTOMER_ID%
    python analytics/generate_summaries.py --customer-id %CUSTOMER_ID%
    cd analytics
)

echo.
echo [INFO] Installing required dependencies...
pip install --quiet scikit-learn joblib numpy python-dateutil 2>nul

echo.
echo ================================================================
echo   Running Advanced Features Test Suite
echo ================================================================
echo.

python test_advanced_features.py %CUSTOMER_ID%

echo.
echo ================================================================
echo   Test Complete!
echo ================================================================
echo.
echo Output files generated in analytics/:
echo   - %CUSTOMER_ID%_risk_model.json
echo   - %CUSTOMER_ID%_cashflow_forecast.json
echo   - %CUSTOMER_ID%_reconciliation.json
echo   - %CUSTOMER_ID%_enhanced_anomalies.json
echo   - %CUSTOMER_ID%_recommendations.json
echo   - %CUSTOMER_ID%_advanced_features_test_report.json
echo.
echo To view in browser:
echo   1. Start backend:  cd api_panel ^&^& python app.py
echo   2. Start frontend: cd frontend ^&^& npm start
echo   3. Navigate to:    http://localhost:3000/customer-profile
echo.

pause
