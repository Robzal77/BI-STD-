# CEA Ranking - Technical Design Document

**Report Name:** CEA Ranking
**Version:** 2.144.878.0 (25.06)+9cca29236de5114792f4d7188221f91ad4a5cc50
**Generated:** February 13, 2026
**Architect:** 40103427

---

## 1. 🏗️ High-Level Architecture

### Star Schema Diagram

*No core fact-dimension relationships found.*

### 🎯 Business Purpose

This report is a business intelligence dashboard providing analytical insights and performance metrics for data-driven decision making.

## 2. 📊 The Data Flow (ETL Analysis)

### Operations Extract Data Pipeline

**Source:** Not explicitly identified in M code

**Transformations:**

## 3. 🧠 Measure Logic (The "Why", not just "What")

### A. Core Financials (Values & Costs)

**Name:** `All scopes carbon emi intensity`
**Logic:** Sum aggregation

**Name:** `Total production volume(Khl)`
**Logic:** Sum aggregation divided by scale factor

**Name:** `Average Emissions Intensity`
**Logic:** Sum aggregation divided by scale factor

**Name:** `Total production volume`
**Logic:** Sum aggregation

**Name:** `Siteranking`
**Logic:** Direct column reference

**Name:** `Bottom Ranking`
**Logic:** Direct column reference

**Name:** `S1 carbon emissions intensity`
**Logic:** Sum aggregation divided by scale factor

**Name:** `S1 Bottom Ranking`
**Logic:** Direct column reference

**Name:** `S1 Siteranking`
**Logic:** Direct column reference

**Name:** `WelcomeMeasure`
**Logic:** Direct aggregation of source column

**Name:** `S2 carbon emissions intensity`
**Logic:** Sum aggregation divided by scale factor

**Name:** `S2 Siteranking`
**Logic:** Direct column reference

**Name:** `S2 Bottom Ranking`
**Logic:** Direct column reference

**Name:** `TEST`
**Logic:** Direct column reference

---

*This Technical Design Document focuses on the core star schema and business logic for CEA Ranking. All utility tables and helper measures have been excluded for clarity.*