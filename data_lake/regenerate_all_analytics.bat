@echo off
REM Regenerate analytics for all customers 00001-00010

echo === Regenerating Analytics for All Customers ===
echo.

FOR %%c IN (CUST_MSM_00001 CUST_MSM_00002 CUST_MSM_00003 CUST_MSM_00004 CUST_MSM_00005 CUST_MSM_00006 CUST_MSM_00007 CUST_MSM_00008 CUST_MSM_00009 CUST_MSM_00010) DO (
    echo Generating analytics for %%c...
    python analytics\generate_summaries.py --customer-id %%c
    echo.
)

echo.
echo === All Analytics Generated Successfully ===
pause
