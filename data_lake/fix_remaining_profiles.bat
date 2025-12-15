@echo off
REM Regenerate profiles that need stronger focus

echo ============================================================================
echo Regenerating Customer Profiles with Stronger Focus
echo ============================================================================
echo.

REM CUST_MSM_00003 - High Debt
echo [CUST_MSM_00003] High Debt Profile
python generate_specialized_customers.py --customer-id CUST_MSM_00003
if errorlevel 1 echo [ERROR] Failed CUST_MSM_00003
echo.

REM CUST_MSM_00004 - High Growth
echo [CUST_MSM_00004] High Growth Profile
python generate_specialized_customers.py --customer-id CUST_MSM_00004
if errorlevel 1 echo [ERROR] Failed CUST_MSM_00004
echo.

REM CUST_MSM_00005 - Stable Income
echo [CUST_MSM_00005] Stable Income Profile
python generate_specialized_customers.py --customer-id CUST_MSM_00005
if errorlevel 1 echo [ERROR] Failed CUST_MSM_00005
echo.

REM CUST_MSM_00006 - High Bounce
echo [CUST_MSM_00006] High Bounce Profile
python generate_specialized_customers.py --customer-id CUST_MSM_00006
if errorlevel 1 echo [ERROR] Failed CUST_MSM_00006
echo.

REM CUST_MSM_00007 - Declining
echo [CUST_MSM_00007] Declining Business Profile
python generate_specialized_customers.py --customer-id CUST_MSM_00007
if errorlevel 1 echo [ERROR] Failed CUST_MSM_00007
echo.

REM CUST_MSM_00008 - Concentration
echo [CUST_MSM_00008] Customer Concentration Profile
python generate_specialized_customers.py --customer-id CUST_MSM_00008
if errorlevel 1 echo [ERROR] Failed CUST_MSM_00008
echo.

echo ============================================================================
echo Regenerating Analytics for All Modified Profiles
echo ============================================================================
echo.

for %%C in (CUST_MSM_00003 CUST_MSM_00004 CUST_MSM_00005 CUST_MSM_00006 CUST_MSM_00007 CUST_MSM_00008) do (
    echo [%%C] Regenerating analytics...
    python analytics/generate_summaries.py --customer-id %%C
)

echo.
echo ============================================================================
echo Checking Metrics
echo ============================================================================
python check_all_metrics.py

echo.
echo ============================================================================
echo Profile Regeneration Complete
echo ============================================================================
pause
