DECLARE @VersionDateToValidate INT;
SET @VersionDateToValidate =
(
    SELECT [DateKey]
    FROM [CarharttDw].[Dimensions].[Days]
    WHERE [CurrentDayOffset] = 0
);

----Sales Demand Units = SalesForecastUnits in EDW---
SELECT TRIM([DT].[YearPeriodMonth]) AS "DatesYear/Period/Month",
       SUM([SCP].[ConstrainedReceiptPlanUnits]) 'Constrained_Receipt_Plan_Units',
	   SUM([SCP].[CurrentTotalReceiptPlanUnits]) 'Total_Receipt_Plan_Units',
	   SUM([SCP].[PlannedProductionUnits]) 'Planned_Production_Units',
	   SUM([SCP].[WorkInProgressUnits]) 'Work_In_Progress_Units',
	   SUM([SCP].[InTransitUnits]) 'In_Transit_Units',
	   SUM([SCP].[SalesForecastUnits]) 'Sales_Demand_Units'    
FROM [CarharttDw].[planning].[SizedWeeklyCombinedPlans] SCP
    INNER JOIN [CarharttDw].[Dimensions].[Days] DT
        ON [DT].[DateKey] = [SCP].[FiscalWeekDateKey]
    INNER JOIN [CarharttDw].[Dimensions].[Products] P
        ON [P].[ProductKey] = [SCP].[ProductKey]
WHERE [SCP].[PlanType] = 'NIGHTLY'
      AND [SCP].[VersionDateKey] = @VersionDateToValidate --Is Key for SavedPlanName
      AND [DT].[CurrentMonthOffset] BETWEEN -1 AND 6
      AND [SCP].[InventorySegment] <> 'ALL' --Visible
      AND [P].[Licensed] <> 'Y' --Visible 
      AND [P].[Licensed] IS NOT NULL --Hidden
GROUP BY [DT].[YearPeriodMonth]
ORDER BY [DT].[YearPeriodMonth];

