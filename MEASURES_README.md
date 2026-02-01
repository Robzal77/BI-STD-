# Power BI Measures Documentation

**Last Refreshed Date:** 2026-02-01 17:28:42

| Model | Table | Measure Name | DAX Formula | Description |
| --- | --- | --- | --- | --- |
| ABInBev_Template | Sales | Sales Amount by Due Date | `CALCULATE(SUM(Sales[Sales Amount]), USERELATIONSHIP(Sales[DueDateKey],'Date'[DateKey])) ` | No description provided |
| AdventureWorks Sales | Sales | Sales Amount by Due Date | `CALCULATE(SUM(Sales[Sales Amount]), USERELATIONSHIP(Sales[DueDateKey],'Date'[DateKey])) ` | No description provided |
| AdventureWorks Sales | Customer | TEST MEASURE | `"TEST"` | No description provided |
| AdventureWorks Sales | Sales | Sales Amount by Due Date | `CALCULATE(SUM(Sales[Sales Amount]), USERELATIONSHIP(Sales[DueDateKey],'Date'[DateKey])) ` | No description provided |
| OFFICIAL_TEMPLATE | Measures | Total Sales | `SUM(Sample_Data[Amount])` | No description provided |
