# Conversion Uplift & Experimentation Analytics

An end-to-end experimentation analytics project that measures the incremental impact of email campaigns on customer visits, conversions, and spend using **MySQL**, **Python**, **Power BI**, **Pixi**, **pytask**, and **pytest**.

This project is built around the **Kevin Hillstrom / MineThatData** email marketing dataset and focuses on a core business question:

> Did the campaign truly create incremental value, and which customer groups responded best?

---

## Business Problem

Marketing teams often know **who converts**, but not necessarily **who converts because of a campaign**.

This project focuses on **incremental impact** rather than raw performance:

- Did the email treatment outperform the control group?
- Which campaign variant performed best?
- Which customer segments responded more positively?
- Where should the business target future campaigns?

The analysis is designed to reflect a realistic experimentation workflow used in **growth**, **CRM**, **product analytics**, and **conversion optimization** settings.

---

## Project Goals

This project was built to:

- design a structured experimentation analytics workflow
- create a normalized analytical schema in MySQL
- automate ingestion, preprocessing, loading, testing, and export steps with Python and Pixi
- validate campaign performance with SQL
- measure uplift relative to control
- prepare reporting datasets for Power BI
- build a portfolio-quality dashboard for stakeholder communication

---

## Tools & Technologies

- **MySQL** — normalized schema design, validation queries, analysis queries, reporting views
- **Python** — ingestion, preprocessing, transformation, export pipeline
- **Power BI** — dashboard design, KPI communication, drilldown reporting
- **Pixi** — environment and task management
- **pytask** — reproducible pipeline automation
- **pytest** — testing preprocessing and data pipeline logic
- **VS Code** — main development environment
- **Git / GitHub** — version control and portfolio packaging

---

## Project Structure

```text
conversion_uplift_experimentation_project/
├── data/
│   ├── final/
│   │   ├── campaign_summary.csv
│   │   ├── channel_campaign_summary.csv
│   │   ├── customer_experiment_detail.csv
│   │   ├── history_segment_campaign_summary.csv
│   │   ├── newbie_campaign_summary.csv
│   │   ├── segment_uplift_summary.csv
│   │   ├── treatment_control_summary.csv
│   │   └── zip_campaign_summary.csv
│   ├── processed/
│   │   └── hillstrom_processed.csv
│   └── raw/
│       └── hillstrom.csv
│
├── notebooks/
│
├── outputs/
│   ├── charts/
│   └── reports/
│       ├── powerbi/
│       │   ├── page_1_executive_overview.png
│       │   ├── page_2_experiment_performance.png
│       │   ├── page_3_customer_segment_insights.png
│       │   └── page_4_detailed_drilldown.png
│       ├── schema/
│       │   ├── conversion_uplift_er_diagram.png
│       └── sql_analysis_summary.md
│
├── powerbi/
│   ├── conversion_uplift_experimentation_dashboard.pbix
│   ├── dashboard_notes.md
│   └── measures_kpis.md
│
├── sql/
│   ├── 01_create_database.sql
│   ├── 02_create_tables.sql
│   ├── 03_load_raw_data.sql
│   ├── 04_validation_queries.sql
│   ├── 05_experiment_analysis_queries.sql
│   ├── 06_reporting_views.sql
│   └── 07_optional_advanced_queries.sql
│
├── src/
│   └── conversion_uplift/
│       ├── __init__.py
│       ├── analysis.py
│       ├── config.py
│       ├── database.py
│       ├── export.py
│       ├── features.py
│       ├── ingest.py
│       ├── load_mysql.py
│       ├── modeling.py
│       ├── preprocess.py
│       └── uplift.py
│
├── tasks/
│   ├── task_build_reporting_tables.py
│   ├── task_ingest_data.py
│   ├── task_load_mysql.py
│   ├── task_model_scoring.py
│   └── task_preprocess_data.py
│
├── tests/
│   ├── test_export.py
│   ├── test_features.py
│   ├── test_ingest.py
│   └── test_preprocess.py
│
├── .env
├── .env.example
├── .gitignore
├── main_project_steps.md
├── pixi.lock
├── pyproject.toml
└── README.md
```

---

## End-to-End Workflow

The project follows a realistic analytics workflow:

1. **Ingest raw data**
2. **Preprocess and enrich the dataset**
3. **Load processed data into MySQL**
4. **Validate schema and loaded records**
5. **Run SQL experiment analysis**
6. **Create reporting views**
7. **Export reporting datasets for Power BI**
8. **Build stakeholder-facing dashboard pages**
9. **Document findings and structure for GitHub**

---

## Dataset

This project uses the **Kevin Hillstrom / MineThatData** email marketing dataset.

The dataset includes customer-level fields such as:

- recency
- historical spend
- channel
- zip code group
- gender indicators
- newbie flag
- experimental segment assignment
- visit outcome
- conversion outcome
- spend outcome

The original experimental groups are transformed into an analytical structure suitable for experimentation reporting and uplift analysis.

---

## MySQL Data Model

A normalized 6-table schema was designed for the experiment workflow:

### Dimension tables
- `dim_zip_code`
- `dim_channel`
- `dim_campaign`
- `dim_customers`

### Fact tables
- `fact_campaign_assignment`
- `fact_campaign_outcomes`

This schema separates:
- customer attributes
- campaign assignment
- experimental outcomes

which makes analysis and reporting cleaner and more scalable.

---

## Entity Relationship Diagram

The project uses a normalized MySQL schema designed for experimentation analytics.  
The schema separates customer attributes, campaign assignment, and campaign outcomes into dimension and fact tables for cleaner validation, analysis, and reporting.

![Entity Relationship Diagram](outputs/reports/schema/conversion_uplift_er_diagram.png)

---

## SQL Layer

The SQL part of the project is split into clear stages:

### 1. Database and table creation
- `01_create_database.sql`
- `02_create_tables.sql`

### 2. Data loading
- `03_load_raw_data.sql`

### 3. Validation
- `04_validation_queries.sql`

Used to verify:
- row counts
- dimension integrity
- joins across schema
- campaign assignment distribution

### 4. Experiment analysis
- `05_experiment_analysis_queries.sql`

Used to evaluate:
- campaign-level visit rate
- conversion rate
- spend per customer
- spend per converter
- treatment vs control comparison
- uplift by campaign
- segmentation by channel, zip code, lifecycle, and customer history

### 5. Reporting views
- `06_reporting_views.sql`

Created reusable reporting views such as:
- customer experiment detail
- campaign summary
- treatment vs control summary
- segment uplift summary
- channel campaign summary
- zip campaign summary
- newbie campaign summary
- history segment campaign summary

### 6. Optional advanced SQL
- `07_optional_advanced_queries.sql`

Reserved for later portfolio extensions such as:
- ranking logic
- window functions
- deeper segment prioritization

---

## Python Pipeline

The Python side handles ingestion, preprocessing, loading, and export.

### Main modules

#### `ingest.py`
Loads and inspects the raw dataset.

#### `preprocess.py`
Builds the canonical processed dataset and creates fields needed for experiment analysis, including:

- `customer_id`
- `campaign_type`
- `binary_treatment_flag`

#### `load_mysql.py`
Loads processed data into the normalized MySQL schema.

#### `export.py`
Exports final reporting datasets for Power BI from MySQL reporting views.

#### `config.py`
Central configuration for paths and environment settings.

#### `database.py`
Database connection helpers.

---

## Reproducibility, Automation, and Testing

This project uses a more professional workflow than a one-off notebook analysis.

### Pixi
Used for environment management and reproducible task execution.

### pytask
Used to support reproducible data workflow thinking and pipeline structure.

### pytest
Used to test core preprocessing and pipeline logic.

This helps make the project more realistic and closer to production-style analytics work.

---

## Running the Project

### 1. Install the environment
```bash
pixi install
```
### 2. Run ingestion
```bash
pixi run ingest
```
### 3. Run preprocessing
```bash
pixi run preprocess
```
### 4. Load data into MySQL
```bash
pixi run lod-mysql
```
### 5. Export final reporting datasets
```bash
pixi run export
```
### 6. Run tests
```bash
pixi run pytest
```

---

## SQL Analysis Highlights

A full written SQL summary is available here:

- `outputs/reports/sql_analysis_summary.md`

### Core findings from SQL

#### Campaign-level performance
- **Mens E-Mail** produced the strongest overall campaign performance
- **Womens E-Mail** also outperformed control
- **No E-Mail** served as the control baseline

#### Treatment vs control
Treatment outperformed control on:
- visit rate
- conversion rate
- average spend per customer

#### Segment-level differences
Performance varied across:
- channel
- zip code group
- customer lifecycle
- historical spend segments

This supports a more targeted campaign strategy rather than a uniform treatment approach.

---

## Power BI Dashboard

The Power BI file is included here:

- `powerbi/conversion_uplift_experimentation_dashboard.pbix`

The dashboard is designed around 4 pages.

---

## Dashboard Page 1 — Executive Overview

Purpose:
- provide a top-level performance summary
- show headline KPIs
- communicate the main business result immediately

Includes:
- total customers
- visit rate
- conversion rate
- avg spend per customer
- campaign comparison charts
- treatment vs control conversion comparison
- executive takeaway

![Executive Overview](outputs/reports/powerbi/page_1_executive_overview.png)

### Main takeaway
Email treatment outperformed control overall, and **Mens E-Mail** delivered the strongest aggregate campaign performance.

---

## Dashboard Page 2 — Experiment Performance

Purpose:
- focus on incremental impact
- compare treatment vs control directly
- show uplift by campaign

Includes:
- treatment and control KPI cards
- absolute visit uplift by campaign
- absolute conversion uplift by campaign
- absolute spend uplift by campaign
- treatment vs control spend comparison
- compact uplift summary table

![Experiment Performance](outputs/reports/powerbi/page_2_experiment_performance.png)

### Main takeaway
Both campaigns generated positive uplift relative to control, but **Mens E-Mail** produced the strongest lift across visits, conversions, and spend per customer.

---

## Dashboard Page 3 — Customer Segment Insights

Purpose:
- show that campaign performance varies across customer groups
- support targeting strategy

Includes:
- conversion rate by channel and campaign
- conversion rate by zip code group and campaign
- conversion rate by customer lifecycle and campaign
- conversion rate by history segment and campaign

![Customer Segment Insights](outputs/reports/powerbi/page_3_customer_segment_insights.png)

### Main takeaway
Campaign performance varies meaningfully across customer segments. Multichannel, rural, higher-history, and existing-customer groups generally show stronger conversion outcomes.

---

## Dashboard Page 4 — Detailed Drilldown

Purpose:
- allow customer-level filtering and exploration
- support drilldown and ad hoc investigation

Includes:
- slicers for campaign, treatment, channel, zip code, lifecycle, and history
- customer-level experiment table
- scatter plot of history vs post-campaign spend by segment

![Detailed Drilldown](outputs/reports/powerbi/page_4_detailed_drilldown.png)

### Main takeaway
This page supports flexible customer-level exploration and makes the dashboard more useful for deeper analysis, not just summary reporting.

---

## Key Business Insights

### 1. Treatment created real incremental value
The treatment group outperformed control on visits, conversions, and spend per customer.

### 2. Mens E-Mail was the strongest campaign variant
Across both summary metrics and uplift metrics, Mens E-Mail delivered the strongest performance.

### 3. Raw performance is not enough
The project emphasizes uplift and control comparison, which is more aligned with real experimentation and CRO thinking than raw conversion ranking alone.

### 4. Segment differences matter
Response differed by:
- channel
- geography
- lifecycle
- history band

This suggests that future campaigns should be more targeted.

---

## Why This Project Matters for My Portfolio

This project reflects the type of analytical workflow used in:

- product analytics
- experimentation analytics
- CRM analytics
- conversion optimization
- marketing measurement

It goes beyond a simple dashboard or notebook project by combining:

- normalized SQL schema design
- Python data pipeline work
- reproducible workflow tooling
- testing
- reporting views
- Power BI stakeholder communication

---

## Future Improvements

Possible next extensions include:

- add optional advanced SQL ranking / prioritization queries
- build uplift modeling comparisons in Python
- compare multiple modeling approaches for treatment effect estimation
- add more advanced DAX measures in Power BI
- create a presentation-ready stakeholder slide deck
- extend dashboard with decision rules for campaign targeting

---

## How to Use This Repository

### SQL users
You can inspect the database design, validation logic, experiment queries, and reporting views in the `sql/` folder.

### Python users
You can reproduce preprocessing, loading, and export logic using the `src/conversion_uplift/` pipeline.

### BI users
You can open the `.pbix` file and explore the four dashboard pages.

---

## Repository Assets

### SQL summary
- `outputs/reports/sql_analysis_summary.md`

### Power BI file
- `powerbi/conversion_uplift_experimentation_dashboard.pbix`

### Power BI screenshots
- `outputs/reports/powerbi/page_1_executive_overview.png`
- `outputs/reports/powerbi/page_2_experiment_performance.png`
- `outputs/reports/powerbi/page_3_customer_segment_insights.png`
- `outputs/reports/powerbi/page_4_detailed_drilldown.png`

---

## Author

**Berke Pehlivan**
Econometrics MSc — University of Bonn  
Data Analytics | SQL | Python | Power BI | Econometrics | Statistics

This project is part of my portfolio work in analytics, experimentation, SQL, Python, and Power BI.