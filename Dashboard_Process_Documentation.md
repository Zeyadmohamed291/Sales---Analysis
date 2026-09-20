# Dashboard Process Documentation

**Project:** Regional Sales Performance Analysis
**Source workbook analyzed:** `Project_Soluation.xlsx` (Excel-native pivot table / pivot chart / Power Pivot dashboard)
**Raw data analyzed:** `Data_Source.xlsx`, `Regions_Sales.xlsx`
**Methodology reference:** Prior Power BI build guide (Phase 1 PDF) — used for workflow structure only, not copied formula-for-formula
**Data period covered:** July 2005 – July 2008

> **A note on verifiability, read before using this document.** `Project_Soluation.xlsx` stores its DAX measures and Power Query (M) transformations inside a compressed, proprietary Power Pivot/xVelocity data-model container (`xl/model/item.data`). This container was inspected directly and contains no recoverable plaintext formula code. Everything in this document that could be **confirmed** — table names, measure names, chart titles/types, slicer fields, cached totals — was extracted directly from the workbook's XML and is marked as such. Anywhere a formula, relationship, or transformation could **not** be confirmed, this document says so explicitly rather than presenting an invented substitute as fact.

---

## 1. Project Overview

**Objective:** Analyze a multi-year bicycle retail transaction dataset (order-line grain) and turn it into a decision-support dashboard covering revenue, cost, profit, and customer performance across regions, products, and sales channels.

**Dataset purpose:** The raw data represents order-line-level sales transactions for a bike/accessories/clothing retailer operating across six countries (Australia, Canada, France, Germany, United Kingdom, United States) between July 2005 and July 2008, with supporting reference data for products, customers, geography, sales staff, pricing, and purchase-decision reasons.

**Dashboard purpose:** Give business stakeholders a single place to answer: *Where is revenue coming from (region, product category, salesperson)? What does it cost, and what's the resulting profit? Who are the customers, and what motivates their purchases?*

**Analytical goals**, as evidenced by the confirmed measure set and pivot breakdowns in the workbook:
- Track headline financial performance (Revenue, Total Cost, Profit, Margin %) over time and by segment.
- Understand the sales funnel by order volume and customer count (No. of Orders, No. of Customers, Average Order Value).
- Break performance down by Region, Product Category/Color, Salesperson, Customer demographics (Gender, Education), and Purchase Reason Type.

---

## 2. Source Data

### 2.1 Files

| File | Role |
|---|---|
| `Data_Source.xlsx` | Primary raw data — transactions and all reference/dimension data |
| `Regions_Sales.xlsx` | Supplementary customer-region mapping — confirmed **fully redundant** with data already in `Data_Source.xlsx` (see §3, Step 7) |
| `Project_Soluation.xlsx` | The built dashboard artifact analyzed for this documentation (pivot tables, pivot charts, slicers, and an embedded Power Pivot data model) |

### 2.2 Tables / sheets and important columns

**`Data_Source.xlsx`**

| Sheet | Grain | Key columns | Notes |
|---|---|---|---|
| `Fact` | 1 row per order line (60,398 rows) | ProductKey, CustomerKey, OrderDate, DueDate, ShipDate, SalesPerson key, SalesOrderNumber, Quantity | No SalesAmount/Cost/Profit column exists here |
| `Reasons` | 1 row per order (27,659 rows) | SalesOrderNumber, SalesReasonName, SalesReasonReasonType | 1:1 with SalesOrderNumber in this dataset |
| `Customers` | 4 separate lookup tables sharing one physical sheet | Block 1 (18,484 rows): CustomerKey, First Name, Last Name, BirthDate, MaritalStatus, Gender, TotalChildren, Education. Block 2 (18,484 rows): CustomerKey, Region. Block 3 (336 rows): GeographyKey, City. Block 4 (336 rows): GeographyKey, State Name | Blocks separated by blank spacer columns on the same sheet |
| `Salespersons` | 10 rows | Salesperson ID, Salesperson Name, Supervisor Name | |
| `Dimproduct` | 295 rows | ProductKey, Color, ModelName, Subcategory, Category | Color contains literal text `'NA'` for 50 rows |
| `Price` | 295 rows | Product Key, Product Name, Jan–Dec (monthly unit price) | Wide, calendar-month format, not year-specific |
| `COST` | 295 rows | Product Key, Product Name, Jan–Dec (monthly unit cost) | Same structure as `Price` |

**`Regions_Sales.xlsx`**: single sheet, Region / GeographyKey / CustomerKey, 18,484 rows.

### 2.3 Data types (as read from the raw workbook)

| Field | Type where inconsistent |
|---|---|
| CustomerKey | Integer in `Fact` and `Regions_Sales.xlsx`; **text** in the `Customers` sheet blocks |
| ProductKey / "Product Key" | Integer in `Fact`; **text** in `Dimproduct`, `Price`, `COST` |
| OrderDate / DueDate / ShipDate | Datetime, clean, no logical inversions (OrderDate ≤ ShipDate ≤ DueDate confirmed for all 60,398 rows) |
| Quantity | Integer, 1–9,000 |

### 2.4 Missing values / duplicates / inconsistent values (confirmed by direct inspection)

- **No true blank/null cells** were found in any populated range of any sheet.
- **Zero full-row duplicates** in `Fact`, `Reasons`, or any dimension table.
- `Dimproduct[Color]` = literal text `'NA'` for 50 of 295 products (~17%) — a placeholder value, not a blank.
- `Reasons[SalesReasonName]` contains `'Television  Advertisement'` with an embedded double space — inconsistent with the other five reason values.
- `Fact[Quantity]` has 177 rows exceeding 500 units (max 9,000) — statistically unusual but not proven erroneous.
- `Regions_Sales.xlsx` duplicates the CustomerKey→Region mapping already present in `Data_Source.xlsx!Customers` — verified row-for-row identical across all 18,484 customers, zero mismatches.

### 2.5 Relevant dimensions and facts

- **Fact:** order-line transactions (`Fact` sheet) — the only true fact table in the raw data.
- **Dimensions:** Product (with Category/Subcategory/Color), Customer (with demographics), Geography (Region/State/City), Salesperson, Sales Reason, and Date (derived from OrderDate/ShipDate/DueDate — no separate raw date table exists).
- **Important business fields confirmed as used in the built dashboard** (see §7–§9): Region, Product Category, Product Color, Salesperson, Customer Gender, Customer Education, Sales Reason Type, Order Month/Quarter/Year.

---

## 3. Data Cleaning

The cleaning requirements below were identified by direct inspection of the raw files. Because the transformation logic inside `Project_Soluation.xlsx` is not recoverable (see the note at the top of this document), each step states the confirmed problem and the transformation the data structurally requires — it does not claim to reproduce the exact steps taken inside that workbook.

| # | Problem | Action | Reason | Result |
|---|---|---|---|---|
| 1 | CustomerKey is integer in `Fact`/`Regions_Sales.xlsx` but text in `Customers` blocks | Cast to one consistent type (Whole Number) before any merge | Mismatched types cause silent join failures or blank results | Reliable joins across every customer-related table |
| 2 | ProductKey/"Product Key" is integer in `Fact` but text in `Dimproduct`/`Price`/`COST` | Cast to Whole Number consistently | Same reason as above | Reliable joins to Product, Price, Cost |
| 3 | `Customers` sheet physically contains 4 unrelated tables side by side | Split into 4 separate queries using fixed ranges, discarding blank spacer columns | A single load would otherwise produce meaningless `Unnamed: n` columns mixing unrelated data | Four clean tables: Customer demographics, Customer→Region, Geography→City, Geography→State |
| 4 | `Salespersons`, `Dimproduct`, `Price`, `COST` each have blank offset rows/columns before their real header | Promote correct header row, trim leading blank columns | Raw import otherwise yields generic `Column1, Column2…` headers | Correctly labeled columns |
| 5 | `Dimproduct[Color]` = `'NA'` for 50 rows | Retained as a literal category value (no conversion applied) | No business rule was available to justify converting it to a blank; treating an existing text value as if it were missing would be an assumption this analysis cannot verify | 'NA' stands as its own Color category, consistent with how it appears in the source |
| 6 | `Reasons[SalesReasonName]` = `'Television  Advertisement'` (double space) | Whitespace trimmed to a single space | Prevents this value being treated as a category distinct from a correctly spaced entry | Consistent, de-duplicated category values |
| 7 | `Regions_Sales.xlsx` duplicates the Region mapping already inside `Data_Source.xlsx!Customers` | Data_Source.xlsx's embedded Customer→Region block was treated as the single source of truth; `Regions_Sales.xlsx` was not loaded as a second copy of the same relationship | Loading both would create a duplicate or ambiguous many-to-many join on CustomerKey | One unambiguous Customer→Region relationship |
| 8 | `Fact` has no SalesAmount, UnitPrice, or Cost field | Fact was extended with derived SalesAmount and TotalCost, computed from Quantity against the matching ProductKey + calendar month in `Price`/`COST` | The Revenue, Total Cost, and Profit measures confirmed in the dashboard's data model (§7) cannot exist without a monetary value on each order line | Every order line carries a computed SalesAmount and TotalCost |
| 9 | 177 Quantity values exceed 500 units | Retained as-is; not capped, deleted, or flagged as erroneous | No independent evidence (business confirmation) was available to classify these as errors rather than legitimate bulk/wholesale orders | Original transaction volumes preserved |
| 10 | `Price`/`COST` are month-only (Jan–Dec), not year-specific | Applied as a recurring calendar-month rate across all order years (2005–2008) | This is the only interpretation the monthly-only structure of the source table supports; no year-specific pricing data exists anywhere in the source | Every order line's month determines which monthly rate applies, regardless of year |

**Explicitly unverifiable:** whether the actual query steps inside `Project_Soluation.xlsx` performed these exact operations, in this order, cannot be confirmed — the M code itself is not recoverable. Steps 5, 9, and 10 in particular reflect a documented default position taken in the absence of business confirmation, not a verified business rule.

---

## 4. Power Query Transformations

`xl/connections.xml` inside `Project_Soluation.xlsx` confirms **10 named Power Query queries** exist in the workbook:

`Fact_Sales`, `Dim_Customer`, `Dim_Region`, `Dim_City`, `Dim_State`, `Dim_SalesPerson`, `Dim_Reasons`, `Product`, `Dim_Product(D)`, `Cost(D)`

This query list is consistent with the raw-data structure found in §2 — separate customer, region, city, and state queries matching the four sub-tables inside the `Customers` sheet (plus `Regions_Sales.xlsx`), and product/cost-related queries matching `Dimproduct`/`Price`/`COST`. No standalone "Price" query name exists, which suggests pricing was merged directly into `Fact_Sales` rather than kept as its own loaded table — this is inferred from the naming pattern, not confirmed.

**M code could not be extracted.** The Power Query mashup package for an Excel Data Model is stored inside the same unreadable compressed container as the DAX measures (`xl/model/item.data`); direct byte-level inspection found no plaintext M syntax.

The table below documents each **required** transformation, based on what the raw data structurally demands (§3) and the confirmed query names — not on recovered M code. Where a transformation is simple and unambiguous, illustrative syntax is provided and clearly labeled as such; it is representative of the step type, not extracted from the source file.

| Transformation | Purpose | M code |
|---|---|---|
| Change Type — CustomerKey, ProductKey | Cast to Whole Number for reliable joins (§3, Steps 1–2) | *Illustrative, not extracted:* `Table.TransformColumnTypes(Source, {{"CustomerKey", Int64.Type}})` |
| Split `Customers` sheet into 4 range-based queries | Extract each embedded lookup table separately (§3, Step 3) | Not verifiable — exact range/offset logic used in the source is unrecoverable |
| Promote Headers / Remove Top Rows | Correct header row on `Salespersons`, `Dimproduct`, `Price`, `COST` (§3, Step 4) | *Illustrative, not extracted:* `Table.PromoteHeaders(Table.Skip(Source, n))` |
| Trim Text — SalesReasonName | Remove the double-space inconsistency (§3, Step 6) | *Illustrative, not extracted:* `Table.TransformColumns(Source, {{"SalesReasonName", Text.Trim}})` |
| Unpivot Columns — `Price`, `COST` | Convert wide Jan–Dec columns into a long Month/Value structure so a price/cost can be looked up by ProductKey + month | Not verifiable — required by the data shape, but the exact step configuration in the source is unrecoverable |
| Merge Queries — Fact ↔ unpivoted Price/COST | Attach a unit price and unit cost to each order line by ProductKey + Month(OrderDate) (§3, Step 8) | Not verifiable |
| Add Column — SalesAmount, TotalCost | `Quantity × Price` and `Quantity × Cost` | Not verifiable |
| Merge Columns — First Name + Last Name | Produce the `Full Name` field confirmed to exist on `Dim_Customer` in the data model (§7) | Not verifiable — confirmed only by the field's presence in the pivot cache, not by recovered M code |

---

## 5. Data Model

### 5.1 Tables confirmed to exist in the model

Extracted directly from the workbook's pivot-cache field references (`[TableName].[FieldName]` syntax used by Excel OLAP pivots against the internal data model):

| Table | Confirmed fields (from pivot caches) |
|---|---|
| `Fact_Sales` | OrderDate (exposed at Year, Quarter, and Month granularity) |
| `Dim_Customer` | Region, State Name, Gender, Education, Full Name |
| `Dim_SalesPerson` | Salesperson Name |
| `Dim_Reasons` | SalesReasonReasonType |
| `Product` | Category, Subcategory, Color |

`Dim_City`, `Dim_Product(D)`, and `Cost(D)` are confirmed to exist as Power Query connections (§4) but **no field from them appears in any of the 36 pivot caches inspected** — meaning either they were never used in a visual in this workbook, or they feed the model indirectly (e.g., merged into another query) rather than being dragged directly into a pivot.

### 5.2 Keys, relationships, cardinality, modeling decisions

**Not verifiable.** The relationship graph (join keys, active/inactive status, cross-filter direction, cardinality) is stored inside the same unreadable binary container as the DAX and M code. No relationship definition could be extracted.

What **can** be stated with confidence, because it was verified directly against the raw data (§2.5):
- ProductKey, CustomerKey, GeographyKey, Salesperson ID, and SalesOrderNumber all have 100% referential integrity between `Fact` and their respective dimension tables — meaning a clean one-to-many relationship on each of these keys is structurally supported by the data, even though the actual relationship objects in the model file could not be inspected.
- `Fact_Sales` exposing a Year/Quarter/Month date hierarchy indicates either a marked date table or date-hierarchy grouping was configured — which specific mechanism was used could not be confirmed.

### 5.3 Fact vs. Dimension structure

`Fact_Sales` is the sole fact table (transaction grain). `Dim_Customer`, `Dim_SalesPerson`, `Dim_Reasons`, and `Product` are confirmed dimension tables. `Dim_City`, `Dim_Region`, `Dim_State`, and `Dim_Product(D)`/`Cost(D)` are confirmed to exist as queries but their role in the final loaded model (staging-only vs. loaded dimension) could not be confirmed.

### 5.4 Candidate model diagram

This diagram reflects confirmed table names and structurally-required keys. It is **not** an extracted relationship diagram — no relationship metadata could be recovered.

```
                         ┌────────────────┐
                         │   Fact_Sales    │
                         │ ProductKey      │
                         │ CustomerKey     │
                         │ OrderDate       │
                         │ SalesPersonKey  │
                         │ SalesOrderNumber│
                         │ Quantity        │
                         │ SalesAmount*    │
                         │ TotalCost*      │
                         └───────┬────────┘
        ┌───────────────┬───────┴────────┬────────────────┐
        │               │                │                │
    Product        Dim_Customer    Dim_SalesPerson    Dim_Reasons
 (ProductKey,    (CustomerKey,    (SalespersonID,   (SalesOrderNumber,
  Category,       Region,          Name,             SalesReasonReasonType)
  Subcategory,     State Name,      Supervisor)
  Color)           Gender,
                    Education,
                    Full Name)

  * SalesAmount / TotalCost are derived fields — no such column exists
    in the raw Fact sheet; their presence in the model requires the
    Price/COST merge described in §3 Step 8 and §4.
```

---

## 6. Calculated Columns

**No calculated columns could be confirmed to exist in `Project_Soluation.xlsx`.** No evidence of a calculated column (as distinct from a measure) surfaced in any extractable part of the workbook. This is consistent with the reference methodology's own stated best practice of preferring measures over calculated columns. This section is intentionally left without invented entries, per the requirement not to fabricate DAX.

---

## 7. DAX Measures

`xl/pivotCache/pivotCacheDefinition*.xml` (36 files) confirm **13 measures** exist by name in the workbook's data model — each appears as a `[Measures].[Name]` field reference used by at least one pivot table. **The DAX formula text itself is not recoverable** (stored in the unreadable `item.data` container).

For each measure below: the **name** is confirmed by direct XML extraction. The **DAX** shown is **reconstructed candidate logic** — newly authored to match the confirmed name and, where possible, checked against the actual cached totals on the `Analysis` sheet (also directly extracted, see §11) as a sanity check. It is explicitly **not** a recovered formula and must be validated in Power BI against real data before being trusted as final.

| Name (as stored, including source typos) | Purpose | Reconstructed candidate DAX | Explanation |
|---|---|---|---|
| Revenue | Total sales value | `Revenue = SUM(Fact_Sales[SalesAmount])` | Sums the derived SalesAmount field (§3 Step 8). Cached total ≈ 969,012,427.5 (Analysis sheet, verified). |
| Total Cost | Total cost of goods sold | `Total Cost = SUM(Fact_Sales[TotalCost])` | Sums the derived TotalCost field. Cached total ≈ 637,399,683 (verified). |
| Profit | Revenue minus cost | `Profit = [Revenue] - [Total Cost]` | Straightforward difference. Cached total ≈ 331,612,744.5, and 969,012,427.5 − 637,399,683 = 331,612,744.5 exactly — this candidate formula is **numerically consistent** with the cached data. |
| Total QYT | Total units sold (source typo for "QTY") | `Total QYT = SUM(Fact_Sales[Quantity])` | Cached total ≈ 1,469,602 units (verified). |
| No,Orders | Distinct order count (source typo, comma kept for fidelity) | `No,Orders = DISTINCTCOUNT(Fact_Sales[SalesOrderNumber])` | Cached total = 27,659, matching the row count of the `Reasons` sheet exactly (verified) — consistent with one reason per order. |
| No.Customer | Distinct customer count | `No.Customer = DISTINCTCOUNT(Fact_Sales[CustomerKey])` | Cached total = 18,484, matching the confirmed customer count in the raw data exactly (verified). |
| Rev DailyAverage | Average revenue per calendar day | `Rev DailyAverage = DIVIDE([Revenue], DISTINCTCOUNT(Fact_Sales[OrderDate]))` | Cached value ≈ 862,110.70. Divides revenue by distinct order dates rather than a full date-table day count, since no confirmed date table exists (§5.2). |
| Profit Daily Average | Average profit per calendar day | `Profit Daily Average = DIVIDE([Profit], DISTINCTCOUNT(Fact_Sales[OrderDate]))` | Cached value ≈ 295,029.13; same structural logic as Rev DailyAverage. |
| Average N. of orders per day | Average order volume per day | `Average N. of orders per day = DIVIDE([No,Orders], DISTINCTCOUNT(Fact_Sales[OrderDate]))` | Cached value ≈ 24.61 orders/day. |
| Gross Margen% | Profit margin (source typo for "Margin") | `Gross Margen% = DIVIDE([Profit], [Revenue], 0)` | Cached value ≈ 34.22%. `DIVIDE(...,0)` used instead of `/` to guard against a zero-revenue filter context, per the reference methodology's stated safe-division pattern. |
| Cost% | Cost as a percentage of revenue | `Cost% = DIVIDE([Total Cost], [Revenue], 0)` | Cached value ≈ 65.78%; consistent, since 34.22% + 65.78% = 100.00%. |
| AOV | Average Order Value | `AOV = DIVIDE([Revenue], [No,Orders])` | Cached value ≈ 35,034.25. Uses distinct order count as denominator, not row count, since `Fact_Sales` is at line-item grain and one order spans multiple lines. |
| Customer% | Percentage-of-total customer count within a category context | `Customer% = DIVIDE([No.Customer], CALCULATE([No.Customer], ALL(Product)), 0)` | Used per the Analysis sheet's "Category → Customer%" breakdown (e.g., Accessories ≈ 41.9% of all customers). The `ALL(Product)` pattern is a candidate only — the actual filter-removal table used in the source cannot be confirmed. |

**Validation performed:** Revenue, Total Cost, Profit, Total QYT, No,Orders, No.Customer, and the derived percentages were cross-checked against the `Analysis` sheet's cached pivot values, which were extracted directly and are genuine, unaltered numbers from the workbook (not computed by this documentation). Where a candidate formula reproduces the cached total exactly (Profit, Cost% + Gross Margen% summing to 100%, No,Orders/No.Customer matching row counts), this is noted above as consistency evidence — not proof the exact same DAX syntax was used in the source.

---

## 8. KPIs

The following KPIs are drawn from the `Analysis` sheet's top-line summary block (row 5–6, columns C–N), which is a genuine, extracted cache of computed totals from the workbook — not a re-derivation by this documentation.

| KPI | Business meaning | DAX measure | Interpretation (from the cached value) |
|---|---|---|---|
| Revenue | Total sales value across all transactions | `[Revenue]` | ≈ $969.0M over the full 2005–2008 period |
| Total Cost | Total cost of goods sold | `[Total Cost]` | ≈ $637.4M |
| Profit | Revenue minus cost | `[Profit]` | ≈ $331.6M |
| Gross Margen% | Profit as a share of revenue | `[Gross Margen%]` | ≈ 34.2% — for every $1 of revenue, about $0.34 is retained as profit |
| Cost% | Cost as a share of revenue | `[Cost%]` | ≈ 65.8% — the inverse of Gross Margen% |
| Total QYT | Units sold | `[Total QYT]` | ≈ 1.47M units |
| No,Orders | Distinct orders placed | `[No,Orders]` | 27,659 orders |
| No.Customer | Distinct customers who purchased | `[No.Customer]` | 18,484 customers |
| AOV | Average revenue per order | `[AOV]` | ≈ $35,034 per order |
| Rev DailyAverage | Average daily revenue | `[Rev DailyAverage]` | ≈ $862,111/day |
| Profit Daily Average | Average daily profit | `[Profit Daily Average]` | ≈ $295,029/day |
| Average N. of orders per day | Average daily order volume | `[Average N. of orders per day]` | ≈ 24.6 orders/day |

---

## 9. Dashboard Visuals

The workbook contains **21 pivot charts across 4 chart-bearing pages**, plus one pivot-staging page (`Analysis`) with no charts. Chart type, title, hosting page, and slicer were extracted directly from the drawing/chart/slicer XML relationships. **Important finding, confirmed by tracing each chart's drawing relationship:** the sheet tab names do **not** match the chart content on that tab — this is a genuine inconsistency in the source file, documented as found rather than corrected.

| Page (tab name) | Slicer on page | Chart title | Type | Business purpose (inferred from title) |
|---|---|---|---|---|
| **Revenue** *(tab name matches content)* | Region | Revenue By [Month] | Line | Track revenue trend over time |
| | | Revenue By Sales Person | Bar | Compare individual salesperson performance |
| | | Revenue By Region & Cost | Combo (bar + line) | Compare revenue and cost side-by-side by region |
| | | Revenue & Profit & Cost By Quarter | Area | Show all three financial metrics together over quarters |
| | | Revenue By Category | Doughnut | Show product-category revenue mix |
| | | Revenue By Reason Type | Doughnut | Show which purchase-decision drivers generate the most revenue |
| **Customer** *(tab name; content is Profit-related)* | Year | Profit BY Month | Line | Track profit trend over time |
| | | Profit By Category | Bar | Compare product-category profitability |
| | | Top 10 Customers by Profit | Bar | Identify most profitable individual customers |
| | | Profit By Color | Bar | Compare profitability by product color |
| | | Profit% By State | Pie | Show profit-margin distribution across states |
| **Profit** *(tab name; content is Cost-related)* | Region | Cost By Month & Quarter | Line | Track cost trend over time |
| | | Cost & Profit By Region | Bar | Compare cost and profit together by region |
| | | Cost | Bar | (Title truncated in source; likely a general cost breakdown) |
| | | Cost By Education | Bar | Compare cost associated with customers by education level |
| | | Cost By Color | Doughnut | Show cost distribution by product color |
| **Cost** *(tab name; content is Customer-related)* | Year | Customer & Orders By Month | Line | Track customer/order volume trend over time |
| | | Customer By Category | Bar | Compare customer counts by product category |
| | | Customer By Region | Bar | Compare customer counts by region |
| | | Cuatomer [sic] | Bar | (Title contains a typo in the source; content unconfirmed beyond the title) |
| | | Customer% By Region | Doughnut | Show regional share of the total customer base |

**Fields/measures per individual chart were not extracted.** Confirming exactly which row/column/value fields feed each of the 21 charts would require resolving each chart → pivot cache → field-list chain individually, which was not performed. The **purpose** column above is inferred from chart titles and chart type only, and is explicitly labeled as inference rather than an extracted field binding.

**KPIs:** No dedicated KPI card visuals were found in the chart inventory — the top-line KPI totals (§8) exist only as plain cell values on the `Analysis` staging sheet, not as chart or card objects.

---

## 10. Dashboard Design

**Layout:** Five sheet tabs total — one staging/calculation sheet (`Analysis`, no charts, 12+ pivot summary blocks) and four chart-bearing pages, each built around a specific analytical theme (Revenue, Profit, Cost, Customer) despite the tab-name/content mismatch documented in §9.

**Pages:** `Analysis`, `Revenue`, `Customer`, `Profit`, `Cost` (tab order as stored in the workbook).

**Navigation:** No custom navigation buttons, bookmarks, or drill-through mechanisms were found in the extractable XML; navigation is native Excel sheet-tab switching.

**Filters:** No page-level or visual-level filter definitions beyond the slicers were confirmed.

**Slicers:** 4 slicers total, one per chart-bearing page:
- `Revenue` page → **Region** slicer
- `Customer` page → **Year** (OrderDate Year) slicer
- `Profit` page → **Region** slicer
- `Cost` page → **Year** (OrderDate Year) slicer

Each page alternates between a Region-based and a Year-based slicer rather than every page carrying both — this is the pattern as found, not a design choice made in this documentation.

**KPI cards:** None found as dashboard visual objects (see §9). The confirmed KPI totals exist only as plain values on the `Analysis` sheet.

**Design decisions:** Cannot be attributed with confidence — no design-rationale metadata exists in the workbook. The tab-name/content mismatch (§9) and the absence of KPI card visuals are documented as observed facts, not as intentional design choices, since neither can be verified as deliberate.

---

## 11. Analytical Insights

Every figure below is a genuine cached value extracted directly from the `Analysis` sheet's pivot summaries in `Project_Soluation.xlsx` — none are computed or invented by this documentation.

- **Revenue is heavily concentrated in the United States.** US revenue ≈ $337.2M is the largest of the six regions, followed by Australia (≈$209.6M), Canada (≈$133.5M), UK (≈$109.1M), France (≈$92.1M), and Germany (≈$87.5M). The six regions sum to the confirmed grand total of ≈$969.0M.

- **Salesperson-to-region assignment reveals an organizational pattern.** Five salespeople's individual revenue totals match a single region's total revenue **exactly**: Rabia Silva ($209,595,489.75) = Australia; Kayan Walters ($133,467,293.25) = Canada; Roshan Jeffery ($109,082,235) = United Kingdom; King Landry ($92,141,048.25) = France; Meerab Yang ($87,515,019) = Germany. The remaining five salespeople (Fintan Knott, Aahil Mullen, Harlan Wicks, Ffion Richardson, Ariah Rutledge) sum to $337,211,342.25 — exactly the United States total. This indicates the US market alone is served by five salespeople, while each other region is served by exactly one dedicated salesperson.

- **Accessories dominate revenue despite not being the highest-value category per unit.** Accessories generate ≈$616.2M (63.6% of total revenue) versus Bikes (≈$252.3M) and Clothing (≈$100.5M) — consistent with Accessories also having the largest number of purchasing customers (15,114 of 18,484, or 81.8%), suggesting a high-volume, lower-unit-price product mix rather than a high-margin one. (Per-unit margin by category was not independently confirmed.)

- **Revenue is strongly front-loaded by month.** January (≈$272.2M) and February (≈$133.0M) together account for roughly 42% of the annual pattern shown in the month breakdown, with a sharp decline through mid-year (June ≈$41.6M, September ≈$23.7M — the lowest month) before a smaller uptick toward December (≈$42.5M). This pattern is consistent across the cached totals but the underlying cause (seasonality, promotions, data artifact) is not determinable from the available data alone.

- **Purchase reasons classified as "Other" dominate revenue attribution.** Of $969.0M total revenue, $901.4M (93%) is attributed to reasons typed as "Other," versus $34.7M for Marketing-typed reasons and $32.9M for Promotion-typed reasons — meaning the SalesReasonReasonType field, as currently structured, offers limited discriminating power for marketing-attribution analysis.

- **Customer base skews toward higher education tiers.** Bachelors (5,356) and Partial College (5,064) together represent over 56% of the 18,484-customer base, versus Partial High School (1,581) at the low end.

- **Gender split in revenue is close to even**, with Female customers contributing marginally more (≈$498.8M, 51.5%) than Male customers (≈$470.2M, 48.5%).

No insight beyond what these cached, extracted totals directly support has been included.

---

## 12. Complete End-to-End Workflow

```
Raw Data
  (Data_Source.xlsx: Fact, Reasons, Customers×4, Salespersons, Dimproduct, Price, COST
   Regions_Sales.xlsx: redundant Region mapping)
      ↓
Data Inspection
  (Sheet/column inventory, type-consistency check, referential-integrity
   verification across all keys, duplicate/missing-value scan)
      ↓
Data Cleaning
  (Type casting CustomerKey/ProductKey, splitting the 4-in-1 Customers sheet,
   header promotion, text trimming, redundant-source resolution — §3)
      ↓
Power Query
  (10 confirmed queries: Fact_Sales, Dim_Customer, Dim_Region, Dim_City,
   Dim_State, Dim_SalesPerson, Dim_Reasons, Product, Dim_Product(D), Cost(D);
   unpivot + merge required to derive SalesAmount/TotalCost — §4)
      ↓
Data Modeling
  (Fact_Sales as fact table; Product, Dim_Customer, Dim_SalesPerson,
   Dim_Reasons as confirmed dimensions; relationships structurally
   supported by verified key integrity but not extractable — §5)
      ↓
Calculated Columns
  (None confirmed to exist — §6)
      ↓
DAX Measures
  (13 measures confirmed by name; reconstructed candidate formulas
   validated where possible against cached Analysis-sheet totals — §7)
      ↓
KPIs
  (Revenue, Total Cost, Profit, Gross Margen%, Cost%, Total QYT, No,Orders,
   No.Customer, AOV, Rev/Profit Daily Average, Avg Orders/Day — §8)
      ↓
Visualizations
  (21 pivot charts across 4 pages; line/bar/combo/area/doughnut/pie types — §9)
      ↓
Dashboard
  (5 tabs: Analysis staging sheet + Revenue/Customer/Profit/Cost chart pages,
   4 slicers alternating Region/Year — §10)
      ↓
Insights
  (US revenue concentration, salesperson-region alignment, Accessories volume
   dominance, monthly seasonality, reason-type attribution gap, education
   and gender splits — §11, all sourced from verified cached totals)
```

---

## 13. Reference vs. New Implementation

| Aspect | From the old dashboard (Phase 1 PDF) | New implementation (this project) | Why the change was necessary |
|---|---|---|---|
| **Overall workflow structure** | Import → Model → Date Table → Measures → Visualize → Format → Interactivity → Validate → Publish | Same phase structure used to organize this documentation (§2–§10 mirror this sequence) | The workflow shape is dataset-agnostic and was reused as-is |
| **Star-schema principle** (fact↔dim, many-to-one, single-direction filtering) | Explicitly documented and followed | Adopted as the target modeling approach (§5.4), though the actual relationship objects in the new workbook could not be extracted to confirm cardinality/direction | Same sound modeling principle applies regardless of dataset; only the specific keys differ |
| **`_Measures` table best practice / "prefer measures over calculated columns"** | Explicitly stated and followed in the old build | Consistent with the finding that no calculated columns are confirmed to exist in the new workbook (§6) | Reused principle; the new data happens to support the same pattern |
| **Safe division pattern** (`DIVIDE(x, y, 0)`) | Used throughout the old measure set | Applied in the reconstructed candidate DAX for Gross Margen%, Cost%, and the daily-average measures (§7) | Same defensive pattern; reused because it's a general best practice, not because it was copied from a specific old formula |
| **Pre-existing SalesAmount/Profit/Cost fields on the fact table** | The old FactSales table already contained SalesAmount, Profit, and TotalCost as native columns | The new Fact table has **none** of these — Quantity is the only numeric fact column | This is a structural difference in the source data itself, not a methodology choice; it forces an entirely new transformation (§3 Step 8, §4) that has no equivalent in the old build |
| **Order-date vs. ship-date dual relationship** (USERELATIONSHIP pattern) | A defining feature of the old model | **Not evidenced** anywhere in the new workbook's confirmed fields — Fact_Sales exposes only an OrderDate hierarchy in the pivot caches inspected | Cannot confirm this pattern was reused; it may not apply to the new dataset's confirmed usage, or may exist but simply wasn't dragged into any of the 36 inspected pivots |
| **Excel-native pivot/pivot-chart delivery** | The old reference was a Power BI Desktop build (.pbix) | The new reference (`Project_Soluation.xlsx`) is an **Excel Power Pivot / PivotTable / PivotChart** build, not Power BI | This is a difference in the *reference artifact itself*, not a methodology decision — the new project's actual target platform (Power BI vs. Excel) still needs to be confirmed before implementation |
| **Tab naming discipline** | Not documented as an issue in the old PDF | The new workbook has a confirmed tab-name/content mismatch (§9) | A genuine inconsistency found in the new reference file; noted for correction if this dashboard is rebuilt, not something inherited from the old methodology |
| **Redundant source data** | Not applicable — old PDF assumed pre-cleaned CSVs | `Regions_Sales.xlsx` was found to fully duplicate data already in `Data_Source.xlsx` (§3 Step 7) | A data-supply issue specific to the new project; required a source-of-truth decision that had no equivalent step in the old methodology |

**Summary:** The high-level workflow shape and a handful of general best practices (star schema, measures-over-calculated-columns, safe division) were reused from the old methodology because they are sound regardless of dataset. Everything dataset-specific — the absence of pre-computed financial fields on the fact table, the multi-table-per-sheet raw layout, the redundant region source, and the platform used for the actual reference build — required new analysis and cannot be assumed to carry over from the PDF.
