# 📊 Model - Data Dictionary

**Generated:** 2026-01-31 07:12:55
**Source:** `starter_template\OFFICIAL_TEMPLATE\OFFICIAL_TEMPLATE.SemanticModel`

## 📋 Summary
- **Tables:** 3
- **Measures:** 1
- **Relationships:** 1

---
## 📁 Tables

### DateTable

**Columns:**
| Column | Data Type |
|--------|-----------|
| Date | `dateTime` |
| Year | `int64` |
| Month | `string` |
| Quarter | `string` |

### Measures

**Measures:**
| Measure | Description | Expression |
|---------|-------------|------------|
| **Total Sales** | _No description_ | `SUM(Sample_Data[Amount])` |

### Sample_Data

**Columns:**
| Column | Data Type |
|--------|-----------|
| Category | `string` |
| Amount | `double` |

---
## 📐 All Measures

| Measure | Table | Description |
|---------|-------|-------------|
| **Total Sales** | Measures | _No description_ |

---
## 🔗 Relationships

| From | To | Active | Bi-Di |
|------|-----|--------|-------|
| Sample_Data.DateKey | DateTable.DateKey | ✅ | No |
