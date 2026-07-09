/*======================================================================
 Script Name : 04_Synapse_Serverless_SQL.sql
 Project     : Real-Time Stock Trade Analytics
 Author      : Nitish Sarkar

 Purpose :
    1. Create Analytics Database
    2. Create Database Master Key
    3. Read Gold Delta Lake from ADLS
    4. Create SQL Views for Power BI
    5. Execute Sample Business Queries
=======================================================================*/


---------------------------------------------------------------
-- Step 1 - Create Analytics Database
---------------------------------------------------------------

IF DB_ID('trade_analytics') IS NULL
BEGIN
    CREATE DATABASE trade_analytics;
END
GO


---------------------------------------------------------------
-- Step 2 - Switch Database
---------------------------------------------------------------

USE trade_analytics;
GO


---------------------------------------------------------------
-- Step 3 - Create Database Master Key
---------------------------------------------------------------

IF NOT EXISTS
(
    SELECT *
    FROM sys.symmetric_keys
    WHERE name = '##MS_DatabaseMasterKey##'
)
BEGIN
    CREATE MASTER KEY
    ENCRYPTION BY PASSWORD = '<YOUR_MASTER_KEY_PASSWORD>';
END
GO


---------------------------------------------------------------
-- Step 4 - Create Trade Summary View
---------------------------------------------------------------

CREATE OR ALTER VIEW dbo.vw_trade_summary
AS
SELECT
    symbol,
    total_trades,
    total_quantity,
    average_price,
    total_trade_value,
    gold_processed_time
FROM OPENROWSET
(
    BULK 'https://sttradelakedev.dfs.core.windows.net/trade-data/gold/trade_summary/',
    FORMAT = 'DELTA'
) AS gold;
GO


---------------------------------------------------------------
-- Step 5 - Create Dashboard KPI View
---------------------------------------------------------------

CREATE OR ALTER VIEW dbo.vw_dashboard_summary
AS
SELECT
    SUM(total_trades) AS total_trades,
    SUM(total_quantity) AS total_quantity,
    ROUND(AVG(average_price), 2) AS average_trade_price,
    ROUND(SUM(total_trade_value), 2) AS total_trade_value
FROM dbo.vw_trade_summary;
GO


---------------------------------------------------------------
-- Step 6 - Verify Views
---------------------------------------------------------------

SELECT *
FROM dbo.vw_trade_summary;
GO

SELECT *
FROM dbo.vw_dashboard_summary;
GO


---------------------------------------------------------------
-- Step 7 - Sample Business Queries
---------------------------------------------------------------

SELECT
    symbol,
    total_trades
FROM dbo.vw_trade_summary
ORDER BY total_trades DESC;
GO

SELECT
    symbol,
    total_trade_value
FROM dbo.vw_trade_summary
ORDER BY total_trade_value DESC;
GO

SELECT
    symbol,
    average_price
FROM dbo.vw_trade_summary
ORDER BY average_price DESC;
GO

SELECT
    symbol,
    total_quantity
FROM dbo.vw_trade_summary
ORDER BY total_quantity DESC;
GO