# Conversion Uplift & Experimentation Analytics

An end-to-end experimentation analytics project that measures the incremental impact of email campaigns on customer visits, conversions, and spend using MySQL, Python, uplift modeling, and Power BI.

## Business Problem

Marketing and growth teams often know who is likely to convert, but not necessarily who converts because of a campaign.  
This project focuses on incremental impact:

- Did the email campaign actually work?
- Which treatment performs best?
- Which customer segments respond positively?
- Who should be targeted in future campaigns?

## Project Goals

- Build a reproducible analytics workflow for an experimentation dataset
- Store and query structured data in MySQL
- Perform experiment and uplift analysis in Python
- Create reporting-ready outputs for Power BI
- Practice professional project setup using `pyproject.toml`, Pixi, `pytask`, and `pytest`

## Tools Used

- MySQL
- Python
- VS Code
- Pixi
- pytask
- pytest
- Power BI

## Project Workflow

1. Ingest raw dataset
2. Clean and preprocess customer-level data
3. Load structured tables into MySQL
4. Analyze treatment vs. control performance in SQL and Python
5. Build reporting-ready tables and model outputs
6. Export final datasets for Power BI
7. Build a stakeholder-friendly dashboard

## Project Structure

```text
conversion_uplift_experimentation_project/
├── data/
├── sql/
├── src/
├── tasks/
├── tests/
├── powerbi/
├── outputs/
├── notebooks/
├── .env
├── .env.example
├── .gitignore
├── README.md
├── main_project_steps.md
└── pyproject.toml