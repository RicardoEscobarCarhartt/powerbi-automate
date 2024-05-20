-- Uncomment the following lines to run this in MSSQL Server Management Studio
-- Use CarharttDw;
-- go

/* These are the columns that are compared to power bi dataframe.
YearPeriodMonth
SalesDemandUnits
TotalReceiptPlanUnits
PlannedProductionUnits
*/

-- This query is to be compared to: 'Conectado a Supply.xlsx'
DECLARE @VersionDateToValidate INT;
SET @VersionDateToValidate =
(
    SELECT [DateKey]
    FROM [CarharttDw].[Dimensions].[Days]
    WHERE [CurrentDayOffset] = 0
);
 
----Sales Demand Units = SalesForecastUnits in EDW---
SELECT TRIM([DT].[YearPeriodMonth]) 'YearPeriodMonth',
       SUM([SCP].[SalesForecastUnits]) 'SalesDemandUnits',
       SUM([SCP].[CurrentTotalReceiptPlanUnits]) 'TotalReceiptPlanUnits',
       SUM([SCP].[PlannedProductionUnits]) 'PlannedProductionUnits'
FROM [CarharttDw].[planning].[SizedWeeklyCombinedPlans] SCP
    INNER JOIN [CarharttDw].[Dimensions].[Days] DT
        ON [DT].[DateKey] = [SCP].[FiscalWeekDateKey]
    INNER JOIN [CarharttDw].[Dimensions].[Products] P
        ON [P].[ProductKey] = [SCP].[ProductKey]
WHERE [SCP].[PlanType] = 'NIGHTLY'
      AND [SCP].[VersionDateKey] = @VersionDateToValidate --Is Key for SavedPlanName
      AND [DT].[CurrentYearOffset] IN ( 0, 1 )
      AND [DT].[CurrentSeasonOffset] IN ( 0, 1 )
      AND [SCP].[InventorySegment] <> 'ALL' --Visible
      AND [P].[Licensed] <> 'Y' --Visible
      AND [P].[Licensed] IS NOT NULL --Hidden
GROUP BY [DT].[YearPeriodMonth]
ORDER BY [DT].[YearPeriodMonth];
