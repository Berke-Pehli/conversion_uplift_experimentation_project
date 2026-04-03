
---

## 3. `main_project_steps.md`

Use this as your build tracker:

```md
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
- [ ] Create project folder inside `~/Desktop/Projects`
- [ ] Create all subfolders
- [ ] Create `.env`
- [ ] Create `.env.example`
- [ ] Create `.gitignore`
- [ ] Create `pyproject.toml`
- [ ] Set up Pixi
- [ ] Confirm Pixi commands run correctly
- [ ] Set up pytest
- [ ] Set up pytask

## Phase 4 - Ingestion
- [ ] Add raw dataset to `data/raw/`
- [ ] Build ingestion script
- [ ] Validate source columns
- [ ] Save cleaned raw copy if needed

## Phase 5 - Preprocessing
- [ ] Standardize column names
- [ ] Clean categorical variables
- [ ] Create binary treatment flag
- [ ] Validate nulls and data types
- [ ] Save processed dataset

## Phase 6 - MySQL Load and SQL Layer
- [ ] Create database
- [ ] Create tables
- [ ] Load processed data
- [ ] Run validation queries
- [ ] Build experiment analysis queries
- [ ] Build reporting views

## Phase 7 - Analysis and Modeling
- [ ] Build descriptive experiment analysis
- [ ] Build conversion classification baseline
- [ ] Build uplift model baseline
- [ ] Save scoring outputs

## Phase 8 - Exports and Power BI
- [ ] Export final reporting tables
- [ ] Export model output tables
- [ ] Prepare Power BI input files
- [ ] Write dashboard notes
- [ ] Write measures and KPI definitions

## Phase 9 - Documentation and GitHub
- [ ] Finalize README
- [ ] Add project screenshots later
- [ ] Clean repository structure
- [ ] Commit project to GitHub