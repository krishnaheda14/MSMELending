@echo off
REM Regenerate All Customers with Proper Isolation
REM This script generates realistic per-customer data with proper profiles

echo ============================================================================
echo   MSME Lending - Regenerate All Customers with Proper Isolation
echo ============================================================================
echo.

REM Clean old data
echo [Step 1/3] Cleaning old data...
python cleanup_old_data.py
if errorlevel 1 (
    echo ERROR: Cleanup failed
    exit /b 1
)
echo.

REM Generate base data for all customers
echo [Step 2/3] Generating base data for all customers...
echo.

set CUSTOMERS=CUST_MSM_00001 CUST_MSM_00002 CUST_MSM_00003 CUST_MSM_00004 CUST_MSM_00005 CUST_MSM_00006 CUST_MSM_00007 CUST_MSM_00008 CUST_MSM_00009 CUST_MSM_00010

for %%C in (%CUSTOMERS%) do (
    echo.
    echo [%%C] Generating base data...
    set CUSTOMER_ID=%%C
    python generate_all.py --customer-id %%C
    if errorlevel 1 (
        echo ERROR: Generation failed for %%C
        exit /b 1
    )
)

echo.
echo [Step 3/3] Applying specialized profiles...
echo.

REM Apply profiles (modifying existing data, not regenerating)
echo [CUST_MSM_00001] Baseline - no profile modification
echo.

echo [CUST_MSM_00002] High Seasonality
python apply_profile.py CUST_MSM_00002 high_seasonality
if errorlevel 1 (
    echo ERROR: Profile application failed
    exit /b 1
)

echo.
echo [CUST_MSM_00003] High Debt
python apply_profile.py CUST_MSM_00003 high_debt

echo.
echo [CUST_MSM_00004] High Growth
python apply_profile.py CUST_MSM_00004 high_growth

echo.
echo [CUST_MSM_00005] Stable Income
python apply_profile.py CUST_MSM_00005 stable_income

echo.
echo [CUST_MSM_00006] High Bounce
python apply_profile.py CUST_MSM_00006 high_bounce

echo.
echo [CUST_MSM_00007] Declining
python apply_profile.py CUST_MSM_00007 declining

echo.
echo [CUST_MSM_00008] Customer Concentration
python apply_profile.py CUST_MSM_00008 customer_concentration

echo.
echo [CUST_MSM_00009] High Growth #2
python apply_profile.py CUST_MSM_00009 high_growth

echo.
echo [CUST_MSM_00010] High Seasonality #2
python apply_profile.py CUST_MSM_00010 high_seasonality

echo.
echo ============================================================================
echo   Data generation completed successfully!
echo ============================================================================
echo.
echo Next steps:
echo 1. Run pipeline/clean for each customer
echo 2. Generate analytics for each customer
echo.
echo Example:
echo   cd pipeline
echo   python clean_data.py CUST_MSM_00001
echo   cd ../analytics
echo   python generate_summaries.py --customer-id CUST_MSM_00001
echo.

pause
