# CLAUDE.md — S2T PBI Documentation: דוח תברואה

## Project Context

This project contains a full **S2T (System-to-Technical) documentation** of the Power BI report `___דוח תברואה.pbix` (Sanitation Report).

## What's Here

| File | Description |
|------|-------------|
| `___דוח תברואה.pbix` | Source Power BI report (binary, ~42MB) |
| `S2T_Documentation_דוח_תברואה.md` | Full Markdown S2T documentation (11 sections) |
| `S2T_Documentation_דוח_תברואה.html` | Interactive HTML documentation with dark-theme, sidebar nav |
| `pbix_extracted/` | Extracted PBIX internals used during analysis |

## Report Overview

- **Hebrew name**: דוח תברואה (Sanitation Report)
- **PBI Desktop version**: 2023.05 (format v1.28, OnPrem)
- **Pages**: 15 report pages
- **Data sources**: 4 operational systems + CRM/Dataverse + Events

### Data Source Systems

| Suffix | System | Type |
|--------|--------|------|
| `_It` | Ituran GPS | Vehicle tracking |
| `_Ge` | GE Devices | IoT / device sensors |
| `_Gb` / `_GB` | GB System | Container management |
| `_Gr` | Disposal weighbridge | Tonnage/waste tracking |
| `pws_` | CRM / Dataverse | Incidents, recommendations |
| (none) | Internal / Events | Marks, events, regions |

### Naming Conventions

- `V_` prefix = SQL View (not base table)
- `DimDate` = shared date dimension
- `V_TAV_Regions` = geography + RLS anchor table

## Key Architecture Points

- **Star schema** with multiple fact tables sharing `DimDate` and `V_TAV_Regions`
- **RLS** enforced via `TAV_Users` joined to `V_TAV_Regions.IsVisable`
- **DataModel binary** (XPress9-compressed) was not decompressed — all DAX/relationship info inferred from the report layout layer
- 26 tables identified from `DiagramLayout` file

## pbix_extracted/ Contents

Python scripts used during analysis:

| Script | Purpose |
|--------|---------|
| `extract_fields.py` | Regex-based extraction of all Entity.Property pairs and queryRefs from layout.json |
| `extract_visuals_full.py` | Full visual inventory per page (type, title, tables, fields, filters, slicers) |
| `decompress.py` | Attempted XPress9 decompression of DataModel via Windows NT API (failed — chunked format) |
| `extract_model.py` | Model structure extraction attempt |
| `extract_dax.py` | DAX expression extraction attempt |
| `read_header.py` | DataModel binary header inspection |

Output files:
- `layout.json` — decoded (UTF-16-LE → UTF-8) report layout, 1.17M chars
- `visuals_full.txt` — full visual inventory (1152 lines)
- `datamodel_strings.txt` / `datamodel_utf16.txt` — partial DataModel string extraction

## Notes for Future Work

- To get DAX expressions: use **Tabular Editor** or **DAX Studio** against the live report
- To get exact relationship cardinalities: open in Power BI Desktop → Model view
- Custom visuals present: BCI Calendar, Dual KPI (Microsoft), PayPal KPI Donut Chart, Scrolling Text
