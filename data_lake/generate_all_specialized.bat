@echo off
echo ================================================================================
echo   Generating Specialized Customer Profiles
echo ================================================================================
echo.

REM CUST_MSM_00002 - High Seasonality
echo [1/9] Generating CUST_MSM_00002 (High Seasonality)...
python generate_all.py --customer-id CUST_MSM_00002
python apply_profile.py CUST_MSM_00002 high_seasonality
python analytics/generate_summaries.py --customer-id CUST_MSM_00002
echo.

REM CUST_MSM_00003 - High Debt
echo [2/9] Generating CUST_MSM_00003 (High Debt)...
python generate_all.py --customer-id CUST_MSM_00003
python apply_profile.py CUST_MSM_00003 high_debt
python analytics/generate_summaries.py --customer-id CUST_MSM_00003
echo.

REM CUST_MSM_00004 - High Growth
echo [3/9] Generating CUST_MSM_00004 (High Growth)...
python generate_all.py --customer-id CUST_MSM_00004
python apply_profile.py CUST_MSM_00004 high_growth
python analytics/generate_summaries.py --customer-id CUST_MSM_00004
echo.

REM CUST_MSM_00005 - Stable Income
echo [4/9] Generating CUST_MSM_00005 (Stable Income)...
python generate_all.py --customer-id CUST_MSM_00005
python apply_profile.py CUST_MSM_00005 stable_income
python analytics/generate_summaries.py --customer-id CUST_MSM_00005
echo.

REM CUST_MSM_00006 - High Bounce
echo [5/9] Generating CUST_MSM_00006 (High Bounce)...
python generate_all.py --customer-id CUST_MSM_00006
python apply_profile.py CUST_MSM_00006 high_bounce
python analytics/generate_summaries.py --customer-id CUST_MSM_00006
echo.

REM CUST_MSM_00007 - Declining
echo [6/9] Generating CUST_MSM_00007 (Declining Business)...
python generate_all.py --customer-id CUST_MSM_00007
python apply_profile.py CUST_MSM_00007 declining
python analytics/generate_summaries.py --customer-id CUST_MSM_00007
echo.

REM CUST_MSM_00008 - Customer Concentration
echo [7/9] Generating CUST_MSM_00008 (Customer Concentration)...
python generate_all.py --customer-id CUST_MSM_00008
python apply_profile.py CUST_MSM_00008 customer_concentration
python analytics/generate_summaries.py --customer-id CUST_MSM_00008
echo.

REM CUST_MSM_00009 - High Growth (variant)
echo [8/9] Generating CUST_MSM_00009 (High Growth #2)...
python generate_all.py --customer-id CUST_MSM_00009
python apply_profile.py CUST_MSM_00009 high_growth
python analytics/generate_summaries.py --customer-id CUST_MSM_00009
echo.

REM CUST_MSM_00010 - High Seasonality (variant)
echo [9/9] Generating CUST_MSM_00010 (High Seasonality #2)...
python generate_all.py --customer-id CUST_MSM_00010
python apply_profile.py CUST_MSM_00010 high_seasonality
python analytics/generate_summaries.py --customer-id CUST_MSM_00010
echo.

echo ================================================================================
echo   ✅ ALL SPECIALIZED PROFILES GENERATED
echo ================================================================================
echo.
echo Profile Summary:
echo   CUST_MSM_00001: Baseline (unchanged)
echo   CUST_MSM_00002: High Seasonality
echo   CUST_MSM_00003: High Debt
echo   CUST_MSM_00004: High Growth
echo   CUST_MSM_00005: Stable Income
echo   CUST_MSM_00006: High Bounce Rate
echo   CUST_MSM_00007: Declining Business
echo   CUST_MSM_00008: Customer Concentration
echo   CUST_MSM_00009: High Growth #2
echo   CUST_MSM_00010: High Seasonality #2
echo.
pause
