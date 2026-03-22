# S2T Technical Documentation — דוח תברואה (Sanitation Report)

> **Source file**: `___דוח תברואה.pbix`
> **Extracted from**: PBIX ZIP (Layout JSON + DiagramLayout JSON)
> **DataModel status**: XPress9-compressed binary — DAX expressions NOT directly accessible
> **Created with**: Power BI Desktop (OnPrem), Release 2023.05, Format v1.28
> **Analysis date**: 2026-03-22

---

## 1. Overview

### General Description
This is a **municipal sanitation operations monitoring report** in Hebrew. It tracks and scores multiple sanitation service domains across geographic regions (נפות = districts).

The report integrates **four operational data sources** plus a **CRM system** for public complaints:

| Domain | Hebrew | Data System | Table Suffix |
|--------|--------|-------------|--------------|
| Contractor vehicles (GPS) | רכבי קבלן | Ituran GPS | `_It` |
| Street sweeping carts | טיאוט | GE Devices | `_Ge` |
| Garbage collection routes | פינוי אשפה | GB System | `_Gb` / `_GB` |
| Garbage disposal/dumping | פריקת אשפה | Disposal site weighbridge | `_Gr` |
| Public complaints | פניות | CRM (pws_ tables, Dynamics-like) | — |
| Sanitation events | ארועים | Standalone events table | — |

**Confidence level**: High for structure and report layer. Medium for DAX expressions (inferred from measure names). Low for relationship cardinality (DataModel binary inaccessible).

### Key Subject Areas
- Daily operational scoring per region and per vehicle/cart/truck
- Performance trends over time (% score change)
- Execution vs. planning compliance (bins collected)
- Garbage tonnage monitoring
- Public complaint SLA tracking
- Events/incident logging

---

## 2. Data Model

### 2.1 Tables

| Table Name | Inferred Type | Description | Granularity |
|-----------|--------------|-------------|-------------|
| `V_TAV_FactDailyRoute` | Fact | Ituran GPS — contractor vehicle daily routes | 1 row per vehicle per day |
| `V_TAV_Ge_FactDailyRoute` | Fact | GE Devices — sweeping cart daily routes | 1 row per cart per day |
| `V_TAV_GB_FactDailyRoute` | Fact | GB System — garbage collection route execution | 1 row per route per day |
| `TAV_Gr_Fact_GarbageDisposal` | Fact | Disposal site — garbage dumping records | 1 row per vehicle entry to disposal site |
| `incidents` | Fact | CRM service requests / public complaints | 1 row per complaint |
| `‏‏EventsData` | Fact | Sanitation events / incidents (note: name contains invisible RTL chars) | 1 row per event |
| `pws_caselogs` | Fact/Bridge | Complaint re-open logs | 1 row per case log entry |
| `DimDate` | Dimension | Date table | 1 row per calendar day |
| `V_TAV_Platforms` | Dimension | Ituran — vehicle info (name, license plate) | 1 row per vehicle |
| `V_TAV_Ge_Devices` | Dimension | GE Devices — sweeping cart info (name, contractor, district) | 1 row per device |
| `V_TAV_GB_TrucksInformation` | Dimension | GB — truck info | 1 row per truck |
| `V_TAV_Regions` | Dimension | Geographic regions/districts (נפות); also hosts weighted-average measures | 1 row per region |
| `TAV_Regions_CRM` | Dimension | CRM-linked region dimension | 1 row per region |
| `TAV_Regions_Gr` | Dimension | Disposal site region dimension | 1 row per region |
| `pws_departments` | Dimension | CRM — complaint departments | 1 row per department |
| `pws_quarters` | Dimension | CRM — neighborhood/quarter lookup | 1 row per quarter |
| `pws_casestatus` | Dimension | CRM — case status lookup | 1 row per status |
| `pws_slastatus` | Dimension | CRM — SLA status lookup | 1 row per SLA status |
| `pws_casesubjects` | Dimension | CRM — complaint topic/subject lookup | 1 row per subject |
| `TAV_Providers` | Dimension | Contractor/service providers list | 1 row per provider |
| `TAV_Users` | Dimension | System users (email + assigned region; used for RLS) | 1 row per user |
| `TAV_Marks` | Reference | Scoring rules and marks per provider | 1 row per rule per provider |
| `TAV_Recommendations` | Reference | Recommendations linked to rules and providers | 1 row per recommendation |
| `מדדי רכבים` | Measures table | Vehicle KPI measures group (Hebrew: "Vehicle Metrics") | — |
| `מדדי טיאוט` | Measures table | Sweeping KPI measures group (Hebrew: "Sweeping Metrics") | — |
| `LocalDateTable_c2183593...` | Auto | Auto-created date table (Power BI internal) | 1 row per day |

---

### 2.2 Columns

#### `DimDate`
| Column | Data Type | Calculated | Description |
|--------|-----------|------------|-------------|
| `Date` | Date | No | Calendar date — primary join key |
| `is_yesterday` | Boolean | Yes (assumption) | Flag for "yesterday" filter toggle |
| `טווח תאריכים` | Text | Yes | Calculated label showing selected date range |

#### `V_TAV_FactDailyRoute` (Ituran — Contractor Vehicles)
| Column | Data Type | Calculated | Description |
|--------|-----------|------------|-------------|
| `Date` | Date | No | Route date |
| `StartTime` | DateTime | No | Work shift start time |
| `EndTime` | DateTime | No | Work shift end time |
| `QtyPolygonExit` | Integer | No | Count of exits outside defined work polygon |
| `לוחית זיהוי` | Text | No | Vehicle license plate identifier |
| `Recommendations` | Text | No | Recommendation text for the route |
| `ציון ממוצע_It` | Decimal | Yes (measure) | Average score — Ituran vehicles |
| `ציון ממוצע כל הנפות_It` | Decimal | Yes (measure) | Average score across all regions |
| `אחוז שינוי ציון ממוצע_It` | Decimal | Yes (measure) | % change in score vs. prior period |
| `שעות עבודה_It` | Decimal | Yes (measure) | Total working hours |
| `שעות שהיה_It` | Decimal | Yes (measure) | Hours vehicle was inside work polygon |
| `אחוז שעות שהיה_It` | Decimal | Yes (measure) | % of time inside work polygon |
| `כמות עצירות_It` | Integer | Yes (measure) | Number of stops |
| `קילומטראז'_It` | Decimal | Yes (measure) | Kilometrage driven |

#### `V_TAV_Ge_FactDailyRoute` (GE Devices — Sweeping Carts)
| Column | Data Type | Calculated | Description |
|--------|-----------|------------|-------------|
| `Date` | Date | No | Route date |
| `StartTime` | DateTime | No | Work start time |
| `EndTime` | DateTime | No | Work end time |
| `Nafa` | Text | No | District/region name (native to source) |
| `Recommendations` | Text | No | Recommendation text |
| `ציון ממוצע_Ge` | Decimal | Yes (measure) | Average score — GE sweeping |
| `ציון ממוצע כל הנפות_Ge` | Decimal | Yes (measure) | Average score all regions |
| `אחוז שינוי ציון ממוצע_Ge` | Decimal | Yes (measure) | % change in score |
| `שעות עבודה_Ge` | Decimal | Yes (measure) | Working hours |
| `שעות_עבודה` | Decimal | No/Yes | Working hours (alternative name — possible duplication) |
| `שעות שהיה_Ge` | Decimal | Yes (measure) | Hours in polygon |
| `אחוז שעות שהיה_Ge` | Decimal | Yes (measure) | % hours in polygon |
| `כמות יציאות מפוליגון_Ge` | Integer | Yes (measure) | Polygon exit count |
| `כמות עצירות ארוכות_Ge` | Integer | Yes (measure) | Long stops count |
| `קילומטראז'_Ge` | Decimal | Yes (measure) | Kilometrage |
| `כמות עגלות פעילות_Ge` | Integer | Yes (measure) | Active carts count |
| `אחוז עגלות פעילות_Ge` | Decimal | Yes (measure) | % active carts |
| `ממוצע שעות עבודה לעגלה_Ge` | Decimal | Yes (measure) | Average work hours per cart |

#### `V_TAV_GB_FactDailyRoute` (GB System — Garbage Collection)
| Column | Data Type | Calculated | Description |
|--------|-----------|------------|-------------|
| `RouteDate` | Date | No | Route date |
| `BeginTime` | DateTime | No | Route start time |
| `EndTime` | DateTime | No | Route end time |
| `nvTruckNumber` | Text | No | Truck number (also appears as column + slicer) |
| `nvDriverName` | Text | No | Driver name |
| `nvRegionName` | Text | No | Region name (native to GB source) |
| `nvRouteStatusName` | Text | No | Route status (completed/planned/etc.) |
| `Recommendation` | Text | No | Route recommendation |
| `ציון ממוצע_GB` | Decimal | Yes (measure) | Average score — GB collection |
| `ציון ממוצע כל הנפות_Gb` | Decimal | Yes (measure) | Average score all regions |
| `אחוז שינוי ציון ממוצע_Gb` | Decimal | Yes (measure) | % change in score |
| `כמות פחים מתוכננת` | Integer | Yes (measure) | Planned bin count |
| `כמות פחים שבוצעה` | Integer | Yes (measure) | Actual bins collected |
| `אחוז ביצוע מול תכנון` | Decimal | Yes (measure) | % execution vs. plan |
| `כמות פחים ריקים שרוקנו` | Integer | Yes (measure) | Empty bins that were emptied |
| `אחוז פחים ריקים שרוקנו` | Decimal | Yes (measure) | % empty bins emptied |
| `כמות מסלולים` | Integer | Yes (measure) | Number of routes |
| `טווח תאריכים_Gb` | Text | Yes (measure) | Date range label |

#### `TAV_Gr_Fact_GarbageDisposal` (Disposal Site)
| Column | Data Type | Calculated | Description |
|--------|-----------|------------|-------------|
| `תאריך` | Date | No | Disposal date |
| `יום` | Text/Int | No | Day of week |
| `שכונה` | Text | No | Neighborhood of origin |
| `נהג` | Text | No | Driver |
| `מוביל` | Text | No | Hauling contractor |
| `מס' תעודה` | Text | No | Disposal certificate number |
| `מס' רכב` | Text | No | Vehicle number |
| `שעת כניסה` | DateTime | No | Entry time to disposal site |
| `שעת יציאה` | DateTime | No | Exit time from disposal site |
| `קוד_פנימי` | Text | No | Internal code |
| `סה"כ טונג' אשפה` | Decimal | No/Yes | Total garbage tons |
| `סה"כ משקל אשפה` | Decimal | No | Total garbage weight |
| `ציון ממוצע_Gr` | Decimal | Yes (measure) | Average score — disposal |
| `ציון ממוצע כל הנפות_Gr` | Decimal | Yes (measure) | Average score all regions |
| `אחוז שינוי ציון ממוצע_Gr` | Decimal | Yes (measure) | % change in score |
| `כמות פריקות` | Integer | Yes (measure) | Number of disposal events |
| `ממוצע טונג' יומי` | Decimal | Yes (measure) | Daily average tons |
| `אחוז שינוי ממוצע טונג' אשפה` | Decimal | Yes (measure) | % change in average tons |
| `Measure` | Decimal | Yes (measure) | Fixed/benchmark average tons (reference line) |
| `טווח תאריכים_Gr` | Text | Yes (measure) | Date range label |

#### `incidents` (CRM — Public Complaints)
| Column | Data Type | Calculated | Description |
|--------|-----------|------------|-------------|
| `createdon` | DateTime | No | Complaint creation date |
| `description` | Text | No | Complaint description/body |
| `סוג פניה` | Text | No | Complaint type (values: 'פניות מוקד', 'פניות ציבור') |
| `ציון ממוצע לפניות` | Decimal | Yes (measure) | Average score for complaints |
| `ציון ממוצע כל הנפות לפניות` | Decimal | Yes (measure) | Average score all regions |
| `אחוז שינוי ציון ממוצע לפניות` | Decimal | Yes (measure) | % change in score |
| `כמות פניות` | Integer | Yes (measure) | Total complaint count |
| `כמות פניות פתוחות` | Integer | Yes (measure) | Open complaints |
| `כמות פניות סגורות` | Integer | Yes (measure) | Closed complaints |
| `כמות פניות חורגות` | Integer | Yes (measure) | Overdue/SLA-breaching complaints |
| `כמות פניות מתגלגלות` | Integer | Yes (measure) | Rolling/recurring complaints |
| `אחוז פניות חורגות` | Decimal | Yes (measure) | % overdue complaints |

#### `‏‏EventsData` (Sanitation Events — ⚠️ name has leading invisible RTL Unicode marks)
| Column | Data Type | Calculated | Description |
|--------|-----------|------------|-------------|
| `תאריך הארוע` | Date | No | Event date |
| `סוג ארוע` | Text | No | Event type |
| `שם ארוע` | Text | No | Event name |
| `תאור משאבים תבוראתיים נדרשים` | Text | No | Description of required sanitation resources |
| `משעה` | DateTime | No | Event start time |
| `עד שעה` | DateTime | No | Event end time |
| `מנהל נפה` | Text | No | Region manager |
| `שם שכונה` | Text | No | Neighborhood name |
| `כתובת` | Text | No | Address |
| `מוסר ההודעה` | Text | No | Who reported the event |
| `נפה` | Text | No | Region/district |
| `איש קשר מטעם הארוע` | Text | No | Event contact person |
| `צפי משתמשים` | Integer/Text | No | Expected attendance/user count |
| `הערות` | Text | No | Notes/remarks |
| `כמות ארועים` | Integer | Yes (measure) | Event count |

#### `V_TAV_Platforms` (Ituran Vehicles)
| Column | Data Type | Calculated | Description |
|--------|-----------|------------|-------------|
| `Label` | Text | No | Vehicle name/display label |
| `לוחית רישוי` | Text | No | License plate number |

#### `V_TAV_Ge_Devices` (GE Sweeping Carts)
| Column | Data Type | Calculated | Description |
|--------|-----------|------------|-------------|
| `DeviceName` | Text | No | Cart/device identifier |
| `ContractorName_N` | Text | No | Contractor company name |
| `Nafa` | Text | No | Assigned district |

#### `V_TAV_GB_TrucksInformation` (GB Trucks)
| Column | Data Type | Calculated | Description |
|--------|-----------|------------|-------------|
| `nvTruckNumber` | Text | No | Truck license plate / number |

#### `V_TAV_Regions` (Geographic Regions + Weighted KPIs)
| Column | Data Type | Calculated | Description |
|--------|-----------|------------|-------------|
| `RegionName` | Text | No | District/region name |
| `IsVisable` | Boolean | No | Visibility flag — used for RLS row filter |
| `ממוצע משוקלל` | Decimal | Yes (measure) | Weighted average score for selected region |
| `ממוצע משוקלל כלל הנפות` | Decimal | Yes (measure) | Weighted average score all regions |
| `אחוז שינוי ממוצע משוקלל` | Decimal | Yes (measure) | % change in weighted average |
| `כותרת דוח נפתי` | Text | Yes (measure) | Dynamic title for regional report |
| `ציון ממוצע_It` | Decimal | Yes (measure) | Possibly duplicate — cross-reference |

#### `TAV_Regions_Gr` (Disposal Site Regions)
| Column | Data Type | Calculated | Description |
|--------|-----------|------------|-------------|
| `RegionName` | Text | No | Region name |
| `שכונה` | Text | No | Neighborhood |
| `ממוצע טונג' אשפה יומי` | Decimal | Yes (measure) | Daily average tons per region |

#### `TAV_Users` (User Directory — RLS)
| Column | Data Type | Calculated | Description |
|--------|-----------|------------|-------------|
| `Mail` | Text | No | User email address |
| `RegionName` | Text | No | User's assigned region (used for RLS) |

#### `TAV_Marks` (Scoring Rules)
| Column | Data Type | Calculated | Description |
|--------|-----------|------------|-------------|
| `Provider` | Text | No | Provider/contractor name |
| `Rule` | Text | No | Rule description |
| `Rule_Int` | Integer | No | Numeric rule value |
| `Mark` | Decimal | No | Score/mark assigned |
| `Events` | Text | No | Associated events |

#### `TAV_Recommendations` (Recommendations per Rule)
| Column | Data Type | Calculated | Description |
|--------|-----------|------------|-------------|
| `Provider` | Text | No | Provider name |
| `Rule` | Text | No | Rule description |
| `Rule_Int` | Integer | No | Numeric rule value |
| `Recommendation` | Text | No | Recommendation text |
| `Events` | Text | No | Associated events |

#### `TAV_Providers`
| Column | Data Type | Calculated | Description |
|--------|-----------|------------|-------------|
| `Provider` | Text | No | Provider/contractor name — master list |

#### `pws_departments`
| Column | Data Type | Calculated | Description |
|--------|-----------|------------|-------------|
| `pws_name` | Text | No | Department name |
| `_pws_divisionid_value` | GUID | No | Division ID (filtered to specific GUID in slicers) |

#### `pws_quarters`, `pws_casestatus`, `pws_slastatus`, `pws_casesubjects`
All follow the pattern: `pws_name` (Text, No) — lookup label fields.

#### `pws_caselogs`
| Column | Data Type | Calculated | Description |
|--------|-----------|------------|-------------|
| `כמות פניות שנפתחו מחדש` | Integer | Yes (measure) | Reopened complaints count |
| `אחוז פניות שנפתחו מחדש` | Decimal | Yes (measure) | % reopened complaints |

---

## 3. Relationships

> ⚠️ **Limitation**: Cardinality and cross-filter direction cannot be confirmed — DataModel is XPress9-compressed. Relationships below are **inferred** from visual co-usage patterns.

| From Table | From Column | To Table | To Column | Cardinality (Inferred) | Filter Direction | Notes |
|-----------|-------------|---------|-----------|----------------------|-----------------|-------|
| `DimDate` | `Date` | `V_TAV_FactDailyRoute` | `Date` | 1:M | Single → Fact | Primary date join |
| `DimDate` | `Date` | `V_TAV_Ge_FactDailyRoute` | `Date` | 1:M | Single → Fact | |
| `DimDate` | `Date` | `V_TAV_GB_FactDailyRoute` | `RouteDate` | 1:M | Single → Fact | Column name differs |
| `DimDate` | `Date` | `TAV_Gr_Fact_GarbageDisposal` | `תאריך` | 1:M | Single → Fact | |
| `DimDate` | `Date` | `incidents` | `createdon` | 1:M | Single → Fact | |
| `DimDate` | `Date` | `‏‏EventsData` | `תאריך הארוע` | 1:M | Single → Fact | |
| `V_TAV_Regions` | `RegionName` | `V_TAV_FactDailyRoute` | *(region key)* | 1:M | Single → Fact | RLS anchor |
| `V_TAV_Regions` | `RegionName` | `V_TAV_Ge_FactDailyRoute` | `Nafa` | 1:M | Single → Fact | Cross-source join |
| `V_TAV_Regions` | `RegionName` | `V_TAV_GB_FactDailyRoute` | `nvRegionName` | 1:M | Single → Fact | |
| `V_TAV_Regions` | `RegionName` | `TAV_Gr_Fact_GarbageDisposal` | *(region key)* | 1:M | Single → Fact | |
| `V_TAV_Regions` | `RegionName` | `incidents` | *(region key)* | 1:M | Single → Fact | CRM link |
| `V_TAV_Platforms` | *(key)* | `V_TAV_FactDailyRoute` | *(key)* | 1:M | Single → Fact | Vehicle → daily routes |
| `V_TAV_Ge_Devices` | *(key)* | `V_TAV_Ge_FactDailyRoute` | *(key)* | 1:M | Single → Fact | Cart → daily routes |
| `V_TAV_GB_TrucksInformation` | `nvTruckNumber` | `V_TAV_GB_FactDailyRoute` | `nvTruckNumber` | 1:M | Single → Fact | Truck → routes |
| `TAV_Regions_Gr` | `RegionName` | `TAV_Gr_Fact_GarbageDisposal` | *(region)* | 1:M | Single → Fact | Disposal site region |
| `pws_departments` | *(key)* | `incidents` | *(dept key)* | 1:M | Single → Fact | |
| `pws_quarters` | *(key)* | `incidents` | *(quarter key)* | 1:M | Single → Fact | |
| `pws_casestatus` | *(key)* | `incidents` | *(status key)* | 1:M | Single → Fact | |
| `pws_slastatus` | *(key)* | `incidents` | *(sla key)* | 1:M | Single → Fact | |
| `pws_casesubjects` | *(key)* | `incidents` | *(subject key)* | 1:M | Single → Fact | |
| `TAV_Providers` | `Provider` | `TAV_Marks` | `Provider` | 1:M | Single → Reference | |
| `TAV_Providers` | `Provider` | `TAV_Recommendations` | `Provider` | 1:M | Single → Reference | |
| `TAV_Users` | `RegionName` | `V_TAV_Regions` | `RegionName` | M:1 | Both (assumption) | RLS driver |

---

## 4. Measures (DAX)

> ⚠️ **Note**: DAX expressions are **not accessible** — the DataModel is XPress9-compressed. The following section describes measures by their **inferred logic** based on name, usage context, and display names. No actual DAX code is included.

### 4.1 Scoring Measures (per system)

Each operational system maintains a parallel scoring measure set:

| Measure | Source Table | Inferred Logic | Pattern |
|---------|-------------|---------------|---------|
| `ציון ממוצע_It` | `V_TAV_FactDailyRoute` | Weighted/simple average of vehicle scores | Aggregation |
| `ציון ממוצע_Ge` | `V_TAV_Ge_FactDailyRoute` | Average score for sweeping carts | Aggregation |
| `ציון ממוצע_GB` | `V_TAV_GB_FactDailyRoute` | Average score for garbage collection routes | Aggregation |
| `ציון ממוצע_Gr` | `TAV_Gr_Fact_GarbageDisposal` | Average score at disposal sites | Aggregation |
| `ציון ממוצע לפניות` | `incidents` | Average score for complaint resolution | Aggregation |
| `ציון ממוצע כל הנפות_It` | `V_TAV_FactDailyRoute` | ALL() or ALLSELECTED() over regions | Ratio / Context removal |
| `אחוז שינוי ציון ממוצע_It` | `V_TAV_FactDailyRoute` | DIVIDE(current - prior, prior) | Time intelligence |
| *(Same pattern for `_Ge`, `_Gb`, `_Gr`, `לפניות`)* | | | |

### 4.2 Weighted Average Measures (V_TAV_Regions)

| Measure | Inferred Logic | Pattern |
|---------|---------------|---------|
| `ממוצע משוקלל` | Weighted average combining multiple domain scores for the selected region | Aggregation (composite) |
| `ממוצע משוקלל כלל הנפות` | Same but with context removed (ALL regions) | Ratio / Context removal |
| `אחוז שינוי ממוצע משוקלל` | % change of weighted average vs. prior period | Time intelligence |
| `כותרת דוח נפתי` | Dynamic text measure using SELECTEDVALUE(RegionName) | Dynamic label |

### 4.3 Operational Measures

| Measure | Source Table | Inferred Logic |
|---------|-------------|---------------|
| `שעות עבודה_It` | `V_TAV_FactDailyRoute` | SUM or AVERAGE of working hours |
| `שעות שהיה_It` | `V_TAV_FactDailyRoute` | SUM of hours inside work polygon |
| `אחוז שעות שהיה_It` | `V_TAV_FactDailyRoute` | DIVIDE(שהיה, עבודה) |
| `כמות עצירות_It` | `V_TAV_FactDailyRoute` | SUMX or SUM of stop count |
| `QtyPolygonExit` (sum) | `V_TAV_FactDailyRoute` | SUM(QtyPolygonExit) — used with implicit measure |
| `אחוז ביצוע מול תכנון` | `V_TAV_GB_FactDailyRoute` | DIVIDE(כמות פחים שבוצעה, כמות פחים מתוכננת) |
| `כמות מסלולים` | `V_TAV_GB_FactDailyRoute` | COUNTROWS or DISTINCTCOUNT of routes |
| `סה"כ טונג' אשפה` | `TAV_Gr_Fact_GarbageDisposal` | SUM of tons |
| `ממוצע טונג' יומי` | `TAV_Gr_Fact_GarbageDisposal` | AVERAGEX per day |
| `Measure` (fixed avg) | `TAV_Gr_Fact_GarbageDisposal` | Static benchmark value (reference line) |
| `כמות פניות פתוחות` | `incidents` | COUNTROWS filtered by open status |
| `כמות פניות חורגות` | `incidents` | COUNTROWS filtered by SLA breach |
| `אחוז פניות חורגות` | `incidents` | DIVIDE(חורגות, כמות פניות) |
| `אחוז פניות שנפתחו מחדש` | `pws_caselogs` | DIVIDE(reopened, total) |
| `כמות ארועים` | `‏‏EventsData` | COUNTROWS |

### 4.4 Date / Label Measures

| Measure | Source Table | Inferred Logic |
|---------|-------------|---------------|
| `טווח תאריכים` | `DimDate` | Text concatenation of MIN/MAX dates in selection |
| `טווח תאריכים_Gb` | `V_TAV_GB_FactDailyRoute` | Same but context from GB table |
| `טווח תאריכים_Gr` | `TAV_Gr_Fact_GarbageDisposal` | Same for disposal |
| `is_yesterday` | `DimDate` | Boolean: today-1 flag for toggle slicer |

---

## 5. Calculated Columns

> ⚠️ Cannot be confirmed — DataModel binary not accessible. Based on usage patterns:

| Suspected Column | Table | Evidence | Inferred Logic |
|-----------------|-------|----------|---------------|
| `is_yesterday` | `DimDate` | Used as slicer with boolean-style toggle | `Date = TODAY() - 1` |
| `טווח תאריכים` (if column) | `DimDate` | Used as card display | Possibly calculated column or measure |
| `IsVisable` | `V_TAV_Regions` | Hidden filter for RLS | Boolean flag per region row |

---

## 6. Transformations (Power Query)

> ⚠️ **Power Query M scripts are inside the DataModel binary (XPress9-compressed) and are not accessible.**
> The following is inferred from source system naming patterns.

| Query / Table | Inferred Source | Key Transformations (Assumed) | Notes |
|--------------|----------------|------------------------------|-------|
| `V_TAV_FactDailyRoute` | SQL View (Ituran GPS DB) | Pre-aggregated to daily level; joined to region | Prefix `V_` = View |
| `V_TAV_Ge_FactDailyRoute` | SQL View (GE Devices DB) | Pre-aggregated; includes polygon analysis | Prefix `V_` = View |
| `V_TAV_GB_FactDailyRoute` | SQL View (GB System DB) | Route execution vs. plan | Prefix `V_` = View |
| `V_TAV_Platforms` | SQL View (Ituran) | Vehicle master list | |
| `V_TAV_Ge_Devices` | SQL View (GE Devices) | Cart/device master list | |
| `V_TAV_GB_TrucksInformation` | SQL View (GB System) | Truck info | |
| `V_TAV_Regions` | SQL View / manual | Region list + visibility flag | Used as RLS basis |
| `TAV_Gr_Fact_GarbageDisposal` | SQL Table (disposal DB) | No `V_` prefix — direct table | May not be a view |
| `incidents` | CRM Export / Dataverse | Public complaints data | pws_ prefix = Power Apps / Dataverse naming |
| `pws_*` tables | CRM / Dataverse | Lookup tables from Dynamics CRM | GUID-based foreign keys |
| `‏‏EventsData` | Unknown (manual entry?) | Events/incidents data | Suspicious invisible chars in name |
| `TAV_Marks` | Manual / Excel upload | Scoring rules per provider | Reference data |
| `TAV_Recommendations` | Manual / Excel upload | Recommendations per rule | Reference data |
| `TAV_Providers` | Manual / SQL | Provider master list | |
| `TAV_Users` | Manual / AD / SQL | User-region mapping for RLS | |
| `DimDate` | DAX / Power Query | Auto-generated or manual date table | Has `is_yesterday` custom column |

---

## 7. Report Layer

### 7.1 Pages

| # | Page Name (Hebrew) | English Translation | Purpose |
|---|-------------------|---------------------|---------|
| 1 | ראשי | Main / Home | Navigation page with page navigator + logo |
| 2 | דוח הנהלה | Management Report | Multi-domain summary: Ituran + Complaints + Disposal KPIs by region |
| 3 | דוח הנהלה עם טיאוט | Management Report + Sweeping | Same as above + sweeping carts layer |
| 4 | דוח הנהלה עם פינוי אשפה | Management Report + Garbage Collection | Same + GB collection layer |
| 5 | דוח נפתי | Regional Report | Per-region detail: vehicles + complaints + disposal tables |
| 6 | דוח נפתי עם טיאוט | Regional Report + Sweeping | Regional detail with sweeping carts |
| 7 | דוח נפתי עם פינוי אשפה | Regional Report + Garbage Collection | Regional detail with GB collection |
| 8 | רכבי קבלן | Contractor Vehicles | Deep-dive: Ituran GPS vehicle performance |
| 9 | טיאוט | Street Sweeping | Deep-dive: GE sweeping cart performance |
| 10 | פינוי אשפה | Garbage Collection | Deep-dive: GB garbage collection routes |
| 11 | פריקת אשפה | Garbage Disposal | Deep-dive: disposal site tonnage and scoring |
| 12 | פניות | Complaints | Deep-dive: CRM public complaints SLA tracking |
| 13 | ארועים | Events | Sanitation events log and statistics |
| 14 | ציונים והמלצות | Scores and Recommendations | Rule-based scoring and recommendations reference |
| 15 | Page 2 | (Draft / Auxiliary) | Tonnage analysis — appears to be work-in-progress |

**Navigation pattern**: Pages 2–4 are management-level (one per domain combination); Pages 5–7 are regional-level equivalents. Pages 8–13 are operational drill-down pages per domain. Page 1 hosts the navigation menu.

---

### 7.2 Visuals (Key Visuals per Page)

#### Page: דוח הנהלה (Management Report)
| Visual Type | Title | Fields Used | Description |
|------------|-------|-------------|-------------|
| Card | ציון ממוצע | `V_TAV_FactDailyRoute.ציון ממוצע_It` | Ituran average score KPI |
| Card | ציון ממוצע | `incidents.ציון ממוצע לפניות` | Complaints average score KPI |
| Card | ציון ממוצע | `TAV_Gr_Fact_GarbageDisposal.ציון ממוצע_Gr` | Disposal average score KPI |
| Card | ממוצע משוקלל נפתי | `V_TAV_Regions.ממוצע משוקלל` | Composite weighted score for selected region |
| Card | ממוצע משוקלל כלל הנפות | `V_TAV_Regions.ממוצע משוקלל כלל הנפות` | Composite weighted score all regions |
| Card | אחוז שינוי ממוצע משוקלל נפתי | `V_TAV_Regions.אחוז שינוי ממוצע משוקלל` | % change in composite score |
| pivotTable | (Matrix) | Region + all domain scores + % changes | Cross-domain score matrix by region |
| Slicer | שם נפה | `V_TAV_Regions.RegionName` | Region filter |
| Slicer | תאריך | `DimDate.Date` | Date range filter |
| Slicer | הצג נתוני יום קודם | `DimDate.is_yesterday` | Toggle: show yesterday's data |

#### Page: רכבי קבלן (Contractor Vehicles)
| Visual Type | Title | Fields Used | Description |
|------------|-------|-------------|-------------|
| pivotTable | — | Date hierarchy + Vehicle + all metrics | Full drill-down table by date/vehicle |
| lineChart | ציון ממוצע לפי תאריך | `V_TAV_FactDailyRoute.ציון ממוצע_It` + Date | Score trend over time |
| clusteredBarChart | ציון ממוצע לפי נפה | `V_TAV_FactDailyRoute.ציון ממוצע_It` + Region | Score comparison by region |
| clusteredBarChart | רכבים עם ציון ממוצע גבוה | `V_TAV_FactDailyRoute.ציון ממוצע_It` + License plate | Top-N vehicles by score (filtered) |
| tableEx | — | Full vehicle detail per day | Operational log table |
| Card | כמות יציאות מפוליגון | `SUM(QtyPolygonExit)` | Total polygon violations |
| Card | ציון ממוצע | `ציון ממוצע_It` | KPI card |
| Card | אחוז שעות שהיה | `אחוז שעות שהיה_It` | Time-in-area compliance |
| Card | שעות עבודה | `שעות עבודה_It` | Working hours |
| Card | כמות עצירות ארוכות | `כמות עצירות_It` | Long stops count |
| Slicer | שם רכב | `V_TAV_Platforms.Label` | Vehicle name filter |
| Slicer | לוחית זיהוי | `V_TAV_Platforms.לוחית רישוי` | License plate filter |

#### Page: פינוי אשפה (Garbage Collection)
| Visual Type | Title | Fields Used | Description |
|------------|-------|-------------|-------------|
| Card | כמות פחים שבוצעה | `כמות פחים שבוצעה` | Actual bins collected |
| Card | כמות פחים מתוכננת | `כמות פחים מתוכננת` | Planned bins |
| Card | אחוז ביצוע מול תכנון | `אחוז ביצוע מול תכנון` | Execution rate vs. plan |
| donutChart | כמות מסלולים לפי סטטוס | `nvRouteStatusName` + `כמות מסלולים` | Route status breakdown |
| clusteredBarChart | אחוז ביצוע מול תכנון לפי משאית | `אחוז ביצוע מול תכנון` + truck | Per-truck execution rate |
| lineChart | ציון ממוצע לפי תאריך | `ציון ממוצע_GB` + Date | Score trend |
| tableEx | — | Full route detail | Operational log |

#### Page: פניות (Complaints)
| Visual Type | Title | Fields Used | Description |
|------------|-------|-------------|-------------|
| Card | פניות פתוחות | `כמות פניות פתוחות` | Open complaints count |
| Card | פניות סגורות | `כמות פניות סגורות` | Closed complaints count |
| Card | אחוז פניות חורגות | `אחוז פניות חורגות` | % SLA-breaching complaints |
| Card | אחוז פניות שנפתחו מחדש | `pws_caselogs.אחוז פניות שנפתחו מחדש` | % reopened complaints |
| pivotTable | — | Date + Region + all complaint metrics | Full complaint matrix |
| clusteredBarChart | כמות פניות לפי מחלקה | `pws_departments.pws_name` + `כמות פניות` | Complaints per department |
| clusteredBarChart | פניות פתוחות לפי נושא הפניה | `pws_casesubjects.pws_name` + open count | Open complaints by topic |
| Slicer | סוג פניה | `incidents.סוג פניה` | Filtered to 'פניות מוקד' and 'פניות ציבור' |

---

## 8. Data Lineage (Partial)

```
DimDate.Date
├── → V_TAV_FactDailyRoute [ציון ממוצע_It, שעות עבודה_It, ...]
│       └── → V_TAV_Regions.ממוצע משוקלל (composite KPI)
│               └── → Cards: ממוצע משוקלל נפתי / כלל הנפות
├── → V_TAV_Ge_FactDailyRoute [ציון ממוצע_Ge, שעות עבודה_Ge, ...]
├── → V_TAV_GB_FactDailyRoute [ציון ממוצע_GB, אחוז ביצוע מול תכנון, ...]
├── → TAV_Gr_Fact_GarbageDisposal [ציון ממוצע_Gr, טונג' אשפה, ...]
├── → incidents [ציון ממוצע לפניות, כמות פניות, ...]
└── → ‏‏EventsData [כמות ארועים]

V_TAV_Regions.RegionName (+ IsVisable RLS filter)
├── → V_TAV_FactDailyRoute → Score measures → Management pivot table
├── → incidents → Score measures → Management pivot table
└── → TAV_Gr_Fact_GarbageDisposal → Score measures → Management pivot table

TAV_Users.RegionName (RLS)
└── → V_TAV_Regions.RegionName (restricts visible regions per user)

V_TAV_Platforms → V_TAV_FactDailyRoute
└── → tableEx (vehicle detail tables), slicers

V_TAV_Ge_Devices → V_TAV_Ge_FactDailyRoute
└── → tableEx (sweeping cart detail), slicers

TAV_Providers → TAV_Marks + TAV_Recommendations
└── → tableEx: ציונים והמלצות page
```

**Reusable logic**: The `ציון ממוצע_[suffix]` pattern is duplicated across 4 fact tables with identical semantic meaning but different data sources. This is a **cross-source score normalization pattern** — each domain independently scores itself, then `V_TAV_Regions` aggregates into a composite weighted average.

---

## 9. Observations & Patterns

### 9.1 Naming Conventions
- **Suffix convention**: `_It` = Ituran, `_Ge` = GE Devices, `_Gb/_GB` = GB System, `_Gr` = Garbage disposal — consistent and well-applied
- **Hebrew measures**: Core business measures are in Hebrew; source system columns retain English/mixed naming
- **`V_` prefix**: Tables starting with `V_` are database views (pre-aggregated/joined at source)
- **`pws_` prefix**: CRM tables follow Dataverse/Dynamics naming convention

### 9.2 Repeated Calculation Logic
- The `ציון ממוצע` + `ציון ממוצע כל הנפות` + `אחוז שינוי ציון ממוצע` triplet is repeated **4 times** (one per operational system) — candidate for calculation group or template
- `טווח תאריכים` date range label appears in multiple fact tables (It, Gb, Gr) — likely the same DAX logic duplicated
- "Yesterday toggle" (`DimDate.is_yesterday` slicer) appears on all operational pages — shared UX pattern

### 9.3 Report Architecture Pattern
- 3-tier page structure: Management summary → Regional detail → Operational drill-down
- Pages 2–4 are composites built from the same base (management report), with additional layers toggled via ActionButtons
- RLS implemented via `TAV_Users` (email-based) + `V_TAV_Regions.IsVisable` (region visibility)

### 9.4 Time Intelligence
- Date range filter applied at page level (Relative Date type) on most pages
- `is_yesterday` toggle suggests dual-mode reporting (today vs. yesterday)
- `אחוז שינוי` measures indicate prior-period comparison (likely previous day or previous week)

### 9.5 Modeling Patterns
- ✅ **Star schema** approach per domain (Fact + Date + Dimension)
- ✅ **Multiple fact tables** with shared dimension (`DimDate`, `V_TAV_Regions`) — classic multi-source BI pattern
- ⚠️ **Cross-domain joins** at visual level (e.g., pivotTable on management page merges 4 fact tables directly) — may cause performance issues
- ⚠️ `V_TAV_Ge_FactDailyRoute` has `שעות_עבודה` (with underscore) AND `שעות עבודה_Ge` (with space) — possible duplicate/inconsistency

---

## 10. Risks & Limitations

| Risk | Severity | Description |
|------|---------|-------------|
| DataModel binary inaccessible | High | DAX expressions unavailable — all measure logic is inferred. No relationship cardinality confirmed. |
| `‏‏EventsData` table name | Medium | Table name begins with invisible RTL Unicode marks (`\u200f\u200f`). Causes reference issues and is a hidden defect. |
| Duplicate column names | Medium | `שעות_עבודה` vs `שעות עבודה_Ge` in `V_TAV_Ge_FactDailyRoute` — potential confusion in expressions |
| Missing explicit relationships | Medium | `TAV_Regions_CRM` table is in diagram but no visuals reference it directly — possible orphaned table or legacy artifact |
| Cross-fact table visuals | Medium | Management pivot tables span 4+ fact tables — may generate performance issues with large datasets |
| RLS complexity | Medium | Two-layer RLS (email + region visibility) — risk of data leakage if `IsVisable` filter misconfigured |
| Page naming inconsistency | Low | `Page 2` (English, unnamed) vs all other pages in Hebrew — appears to be an unfinished draft page |
| Calculated column vs. measure ambiguity | Low | Cannot distinguish calculated columns from measures in compressed binary — some labeled as "measure" may be columns |
| `מדדי רכבים` / `מדדי טיאוט` tables | Low | These Hebrew-named tables appear in the diagram but are not referenced in any visual — possibly pure measure tables (DAX disconnected tables) |
| `LocalDateTable_*` internal table | Low | Auto-generated Power BI date table used for date hierarchy on `LocalDateTable_c2183593...` column — should use `DimDate` consistently |
| Typo in measure name | Low | `ממוצע משוקלל כלל הנפות` vs `ממוצע משוקלל כלל הנפות` — one queryRef shows `ממןצע` (with ן instead of ו) — possible typo in measure name |

---

## 11. Improvement Suggestions

### 11.1 Model Structure
- **Eliminate duplicate date table**: `LocalDateTable_c2183593...` co-exists with `DimDate`. All date hierarchies should route through `DimDate` exclusively.
- **Fix invisible chars in `‏‏EventsData`**: Rename to `EventsData` — remove the leading `\u200f\u200f` characters.
- **Review `TAV_Regions_CRM`**: Determine if this table is in use; if not, remove it to reduce model size.
- **Consider a unified region dimension**: `V_TAV_Regions`, `TAV_Regions_CRM`, and `TAV_Regions_Gr` serve similar purposes — could potentially be consolidated.

### 11.2 DAX Optimization
- **Implement Calculation Groups**: The `ציון ממוצע`, `ציון ממוצע כל הנפות`, `אחוז שינוי` pattern repeated across 4 domains — a Calculation Group would eliminate this duplication and ease maintenance.
- **Use a single `טווח תאריכים` measure in `DimDate`**: Currently duplicated in multiple fact tables (`_It`, `_Gb`, `_Gr` variants) — a single measure in `DimDate` with CALCULATE would suffice.
- **Verify `QtyPolygonExit` aggregation**: Currently used as `Sum(V_TAV_FactDailyRoute.QtyPolygonExit)` (implicit measure) — should be formalized as an explicit named measure.

### 11.3 Naming Standardization
- Standardize `ציון ממוצע_GB` vs `ציון ממוצע_Gb` (capitalization inconsistency between `_Gb` and `_GB`)
- Fix typo: `ממןצע משוקלל כלל הנפות` → `ממוצע משוקלל כלל הנפות`
- Standardize `שעות_עבודה` (underscore) vs `שעות עבודה_Ge` (space) in `V_TAV_Ge_FactDailyRoute`

### 11.4 Report / UX
- **`Page 2`**: Either name it properly or delete it — currently an unnamed draft page visible to end users
- **Consolidate pages 2–4**: The three management report variants (plain / +sweeping / +garbage) use action buttons for switching — consider a single page with conditional visibility toggle instead
- **Document the scoring algorithm**: `TAV_Marks` and `TAV_Recommendations` define the scoring rules, but their business logic is opaque without DAX expressions — recommend adding description columns

### 11.5 Documentation Gaps
- No measure descriptions available — critical for new developers
- No source system documentation links in the model
- RLS setup documentation missing — `TAV_Users` population process and `IsVisable` flag management undocumented

---

## Appendix A: Custom Visuals Inventory

| Visual ID | Name | Usage |
|-----------|------|-------|
| `bciCalendarCC0FA2BFE4B54EE1ACCFE383B9B1DE61` | BCI Calendar | Date picker (shown as "unknown" type in some pages — likely date selection calendar) |
| `payPalKPIDonutChart55A431AB15A540ED924ACD72ED8D259F` | **PayPal KPI Donut Chart** (by PayPal ITA) | Double-ring donut chart for displaying percentage KPIs — customizable thickness, colors, font |
| `PBI_CV_3C80B1F2_09AF_4123_8E99_C3CBC46B23E0` | **Dual KPI** (by Microsoft) | Displays two measures over time on a joint timeline — line/area chart with trend, historical hover, and KPI alerts. Used on operational detail pages (shown as "unknown" type in Layout). |
| `ScrollingTextVisual1448795304508` | Scrolling Text | Used on ארועים page for marquee text display |

---

## Appendix B: Report-Level Security Configuration

| Filter | Entity | Property | Type | Visibility | Purpose |
|--------|--------|----------|------|------------|---------|
| Report-level | `TAV_Users` | `RegionName` | Advanced | Visible | Row-level security — limits user to assigned region |
| Report-level | `V_TAV_Regions` | `IsVisable` | Categorical | **Hidden** | Filters out regions flagged as not visible |
| Page-level (most pages) | `DimDate` | `Date` | RelativeDate | Visible | Default date range |
| Page-level (most pages) | `TAV_Users` | `Mail` | Categorical | Visible | User-based data isolation |
