# Main Project Steps

## Phase 1 - Project Proposal
- [x] Choose project idea
- [x] Confirm dataset direction
- [x] Define business problem
- [x] Define analytics scope
- [x] Confirm Hillstrom as Version 1 dataset

## Phase 2 - Dataset Understanding and Schema Design
- [x] Define key KPIs
- [x] Define treatment logic
- [x] Define raw / processed / final data layers
- [x] Define initial MySQL schema
- [x] Define project folder structure

## Phase 3 - Project Setup and Automation
- [x] Create project folder inside `~/Desktop/Projects`
- [x] Create all subfolders
- [x] Create `.env`
- [x] Create `.env.example`
- [x] Create `.gitignore`
- [x] Create `pyproject.toml`
- [x] Set up Pixi
- [x] Confirm Pixi commands run correctly
- [x] Set up pytest
- [x] Set up pytask

## Phase 4 - Ingestion
- [x] Add raw dataset to `data/raw/`
- [x] Build ingestion script
- [x] Validate source columns
- [x] Create ingestion test coverage
- [x] Add ingestion pipeline task

## Phase 5 - Preprocessing
- [x] Standardize column names
- [x] Clean categorical variables
- [x] Create customer ID
- [x] Create campaign type
- [x] Create binary treatment flag
- [x] Validate nulls and data types
- [x] Save processed dataset
- [x] Create preprocessing test coverage
- [x] Add preprocessing pipeline task

## Phase 6 - MySQL Load and SQL Layer
- [x] Create database
- [x] Create tables
- [x] Load processed data
- [x] Run validation queries
- [x] Build experiment analysis queries
- [x] Build reporting views
- [x] Export final reporting tables
- [x] Add MySQL load task
- [x] Add reporting export task

## Phase 7 - Python Analysis and Feature Engineering
- [x] Build descriptive experiment analysis in Python
- [x] Save summary outputs and charts
- [x] Build feature engineering pipeline
- [x] Save modeling-ready datasets
- [x] Create feature test coverage
- [x] Add feature pipeline task

## Phase 8 - Baseline Modeling
- [x] Build conversion classification baseline
- [x] Build visit classification baseline
- [x] Build spend regression baseline
- [x] Evaluate classification models with PR-AUC and related metrics
- [x] Save modeling outputs and charts
- [x] Create modeling test coverage
- [x] Add modeling pipeline task

## Phase 9 - Uplift Modeling
- [x] Build uplift model baseline
- [x] Score customer-level uplift
- [x] Build uplift decile summary
- [x] Add observed uplift validation by decile
- [x] Build segment-level uplift summary
- [x] Save uplift outputs and charts
- [x] Create uplift test coverage
- [x] Add uplift pipeline task

## Phase 10 - Power BI
- [x] Prepare Power BI input files
- [x] Write dashboard notes
- [x] Write measures and KPI definitions
- [x] Build Executive Overview page
- [x] Build Experiment Performance page
- [x] Build Customer Segment Insights page
- [x] Build Detailed Drilldown page
- [x] Save dashboard screenshots

## Phase 11 - Testing and Reproducibility
- [x] Add config tests
- [x] Add database helper tests
- [x] Add export tests
- [x] Add lightweight pipeline integration test
- [x] Confirm pytest suite passes
- [x] Confirm pytask pipeline passes

## Phase 12 - Documentation and GitHub
- [x] Write SQL analysis summary
- [x] Organize project docs into `docs/`
- [x] Finalize README
- [x] Update project structure tree
- [x] Clean repository structure
- [ ] Final review of tracked vs ignored files
- [ ] Final GitHub push after documentation cleanup

## Future Improvements
- [ ] Compare multiple uplift modeling approaches
- [ ] Add gain / Qini-style uplift evaluation
- [ ] Improve spend modeling with alternative target transformations
- [ ] Add optional advanced SQL prioritization queries
- [ ] Create presentation-ready stakeholder slides
- [ ] Extend dashboard with campaign targeting decision rules