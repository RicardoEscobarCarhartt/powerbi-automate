DECLARE @VersionDateToValidate INT;
SET @VersionDateToValidate =
(
    SELECT [DateKey]
    FROM [CarharttDw].[Dimensions].[Days]
    WHERE [CurrentDayOffset] = 0
);

-----BOP and EOP
WITH WeeksOfPeriods
AS (SELECT [EVT].[YearPeriodMonth],
           MIN([EVT].[WeekOfYear]) AS FirstWeekOfPeriod,
           MAX([EVT].[WeekOfYear]) AS LastWeekOfPeriod
    FROM [Dimensions].[Days] EVT
    WHERE [EVT].[CurrentMonthOffset] BETWEEN -1 AND 6 
    GROUP BY [EVT].[YearPeriodMonth]),
     ----BOP, use min Date
     BOP
AS (SELECT [DT].[YearPeriodMonth],
           [DT].[WeekOfYear],
           SUM([SCP].[BeginningInventoryUnitsActual]) AS 'BOP_Inventory_Units'
    FROM [planning].[SizedWeeklyCombinedPlans] SCP
        INNER JOIN [Dimensions].[Days] DT
            ON [DT].[DateKey] = [SCP].[FiscalWeekDateKey]
        INNER JOIN WeeksOfPeriods LW
            ON [DT].[YearPeriodMonth] = [LW].[YearPeriodMonth]
               AND [DT].[WeekOfYear] = [LW].[FirstWeekOfPeriod] -- Cambio hecho aqu�
        INNER JOIN [Dimensions].[Products] P
            ON [P].[ProductKey] = [SCP].[ProductKey]
    WHERE [SCP].[PlanType] = 'NIGHTLY'
          AND [SCP].[VersionDateKey] = @VersionDateToValidate
          AND [SCP].[InventorySegment] <> 'ALL'
          AND [P].[Licensed] <> 'Y' --Visible 
          AND [P].[Licensed] IS NOT NULL --Hidden
    GROUP BY [DT].[YearPeriodMonth],
             [DT].[WeekOfYear])

--- EOP and measures that use MAX date
SELECT TRIM([DT].[YearPeriodMonth]) AS "DatesYear/Period/Month",
       [B].[BOP_Inventory_Units],
       SUM([SCP].[EndingInventoryUnitsActual]) AS 'EOP_Inventory_Units',
       SUM([SCP].[TargetWeeksOfCoverageUnits]) AS 'Forward_Weeks_Of_Coverage_Units',
	   SUM([SCP].[SafetyStockUnits]) AS 'Safety_Stock_Units'
FROM [CarharttDw].[planning].[SizedWeeklyCombinedPlans] SCP
    INNER JOIN [Dimensions].[Days] DT
        ON [DT].[DateKey] = [SCP].[FiscalWeekDateKey]
    INNER JOIN WeeksOfPeriods LW
        ON [DT].[YearPeriodMonth] = [LW].[YearPeriodMonth]
           AND [DT].[WeekOfYear] = [LW].[LastWeekOfPeriod]
    INNER JOIN [Dimensions].[Products] P
        ON [P].[ProductKey] = [SCP].[ProductKey]
    LEFT JOIN BOP B
        ON [DT].[YearPeriodMonth] = [B].[YearPeriodMonth]
           AND [LW].[FirstWeekOfPeriod] = [B].[WeekOfYear]
WHERE [SCP].[PlanType] = 'NIGHTLY'
      AND [SCP].[VersionDateKey] = @VersionDateToValidate
      AND [SCP].[InventorySegment] <> 'ALL'
      AND [P].[Licensed] <> 'Y' --Visible 
      AND [P].[Licensed] IS NOT NULL --Hidden
GROUP BY [DT].[YearPeriodMonth],
         [B].[BOP_Inventory_Units]
ORDER BY [DT].[YearPeriodMonth];
