-- This query is to be compared to: 'Conectado a Supply.xlsx'
SELECT [DT].[ActualDate] as [Version Date],
       [EVT].[YearPeriodMonth],
       SUM(SCP.SalesForecastUnits) 'SalesDemandUnits',
       SUM(SCP.CurrentTotalReceiptPlanUnits) 'TotalReceiptPlanUnits',
       SUM(SCP.PlannedProductionUnits) 'PlannedProductionUnits',
       SUM([SCP].[HighSurplusUnits]) [HighSurplusUnits],
       SUM([SCP].[LowSurplusUnits]) [LowSurplusUnits],
       SUM([SCP].[InventoryTargetRiskUnits] - [SCP].[HighRiskUnits]) AS 'LowRisk',
	   ---Max Date of Period
	   SUM([SCP].[HighRiskUnits]) AS 'HighRisk',
       SUM([SCP].[InventoryTargetRiskUnits]) 'Inventory Target Risk Units',
       SUM([SCP].[InventoryTargetSurplusUnits]) 'Inventory Target Surplus Units'
FROM [CarharttDw].[Planning].[SizedWeeklyCombinedPlans] SCP
    INNER JOIN [Dimensions].[Days] DT
        ON [SCP].[VersionDateKey] = [DT].[DateKey]
    INNER JOIN [Dimensions].[Days] EVT
        ON [EVT].[DateKey] = [SCP].[FiscalWeekDateKey]
    INNER JOIN [Dimensions].[Products] P
        ON [P].[ProductKey] = [SCP].[ProductKey]
WHERE
    --View Filters
    [SCP].[PlanType] = 'NIGHTLY'
    AND [SCP].[InventorySegment] != 'ALL'
    AND [SCP].[ExtendedEOP] = 'N'
    --PBI Filters Hidden
    and [P].[Department] in ( 'Men''s', 'Women''s', 'Personal Protective' ) --Hidden
    AND EVT.YearPeriodMonth IS NOT NULL
    AND [EVT].[CurrentYearOffset] IN ( 0,1)
    and [EVT].[CurrentSeasonOffset] IN (0,1)
    and [P].[StockCategory] = 'A'
    and [P].[SalesStatus] <> 'Z1'
    and P.StillInERP = 'Y' --FirstQuality
    --PBI Visible Filters
    AND [SCP].[VersionDateKey] =
    (
        SELECT [DateKey] FROM [Dimensions].[Days] WHERE [CurrentDayOffset] = 0
    )    
GROUP BY [DT].[ActualDate],
         [EVT].[YearPeriodMonth]
ORDER BY [EVT].[YearPeriodMonth];