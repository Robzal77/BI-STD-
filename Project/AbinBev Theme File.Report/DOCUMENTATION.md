# AbinBev Theme File - Report Documentation

**Auto-generated:** 2026-02-01 19:07:19
**Developer:** robza

---

## Overview

This document provides comprehensive documentation for the **AbinBev Theme File** Power BI report.

## Data Model

### Relationships

- **Total Relationships:** 8
- **Bidirectional Filters:** 0

## Measures

### Table: Customer

#### test measure

**Description:** this is a test measure

### Table: Sales

#### Sales Amount by Due Date

**Description:** Sales amount by Due Date

**DAX Formula:**
```dax
			CALCULATE(SUM(Sales[Sales Amount]), USERELATIONSHIP(Sales[DueDateKey],'Date'[DateKey]))
```


**Total Measures:** 2

## Governance Compliance

*Run `Run_Governance_Check.bat` to verify compliance status.*

## Change History

| Date | Developer | Changes |

|------|-----------|----------|

| 2026-02-01 | robza | Initial documentation generated |
