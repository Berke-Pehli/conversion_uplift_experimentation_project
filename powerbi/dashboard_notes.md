# Power BI Dashboard Notes

## 1. Dashboard Purpose

The purpose of this dashboard is to communicate the results of the email experimentation analysis in a stakeholder-friendly format.

The dashboard should help answer the following business questions:

- Did the email campaigns outperform the control group?
- Which campaign performed best?
- How much uplift did the campaigns generate?
- Which customer segments responded more positively?
- How should the business think about future targeting?

This dashboard is designed to support product, CRM, and growth-style decision making.

---

## 2. Recommended Dashboard Structure

The dashboard should contain **4 main pages**:

1. **Executive Overview**
2. **Experiment Performance**
3. **Customer Segment Insights**
4. **Detailed Drilldown**

This keeps the report organized and avoids overloading a single page.

---

## 3. Page 1 — Executive Overview

### Goal
Provide a quick top-level summary for a stakeholder who wants the main conclusion immediately.

### Main business question
Did the campaign work, and which campaign performed best?

### Recommended visuals
- KPI cards:
  - total customers
  - overall visit rate
  - overall conversion rate
  - overall average spend per customer
- clustered bar chart:
  - customer count by campaign segment
- grouped column chart:
  - visit rate by campaign
- grouped column chart:
  - conversion rate by campaign
- grouped column chart:
  - average spend per customer by campaign
- short text box with key takeaway

### Recommended data sources
- `campaign_summary.csv`
- `treatment_control_summary.csv`

### Key takeaway to communicate
Email treatment outperformed control overall, and Mens E-Mail was the strongest aggregate campaign.

---

## 4. Page 2 — Experiment Performance

### Goal
Focus on treatment vs control and uplift interpretation.

### Main business question
How much incremental impact did the campaigns create?

### Recommended visuals
- KPI cards:
  - treatment visit rate
  - treatment conversion rate
  - treatment avg spend per customer
  - control visit rate
  - control conversion rate
  - control avg spend per customer
- table or matrix:
  - campaign segment KPI summary
- bar chart:
  - absolute visit uplift by campaign
- bar chart:
  - absolute conversion uplift by campaign
- bar chart:
  - absolute spend uplift by campaign
- optional waterfall or decomposition view for spend uplift

### Recommended data sources
- `campaign_summary.csv`
- `treatment_control_summary.csv`
- `segment_uplift_summary.csv`

### Key takeaway to communicate
Both campaigns outperformed control, but Mens E-Mail generated the strongest lift.

---

## 5. Page 3 — Customer Segment Insights

### Goal
Show that campaign performance is not uniform across all customers.

### Main business question
Which segments respond better, and where should targeting be prioritized?

### Recommended visuals
- grouped bar chart:
  - performance by channel and campaign
- grouped bar chart:
  - performance by zip code and campaign
- grouped bar chart:
  - performance by newbie flag and campaign
- grouped bar chart:
  - performance by history segment and campaign
- optional heatmap or matrix:
  - channel × campaign
  - zip code × campaign
  - history segment × campaign

### Recommended data sources
- `channel_campaign_summary.csv`
- `zip_campaign_summary.csv`
- `newbie_campaign_summary.csv`
- `history_segment_campaign_summary.csv`

### Key takeaway to communicate
Response varies meaningfully across customer segments, which supports more targeted treatment strategies.

---

## 6. Page 4 — Detailed Drilldown

### Goal
Provide a flexible exploration page for deeper filtering and detailed inspection.

### Main business question
What happens when we filter the customer-level data by different attributes?

### Recommended visuals
- detailed table:
  - customer-level experiment detail
- slicers:
  - segment
  - campaign_type
  - binary_treatment_flag
  - zip_code_name
  - channel_name
  - newbie
  - history_segment
- optional scatter plot:
  - history vs spend
- optional distribution chart:
  - spend by campaign
- optional table for filtered customer counts and outcomes

### Recommended data source
- `customer_experiment_detail.csv`

### Key takeaway to communicate
This page supports exploration rather than summary. It should help identify more specific patterns and support stakeholder questions.

---

## 7. Recommended slicers across the report

Suggested slicers:
- campaign segment
- campaign type
- binary treatment flag
- zip code
- channel
- newbie
- history segment

These slicers should be used carefully so the report remains readable.

---

## 8. Recommended KPI logic

Main KPIs to emphasize:
- customer count
- visit rate
- conversion rate
- average spend per customer
- total spend
- absolute uplift
- relative lift

These should be kept consistent across pages.

---

## 9. Storytelling order

The report should tell a clear story in this order:

1. **Did treatment work overall?**
2. **Which campaign performed best?**
3. **How large was the uplift?**
4. **Which segments responded differently?**
5. **Why should the business move toward more targeted decision making?**

This sequence is important because it turns technical analysis into a business narrative.

---

## 10. Dashboard design notes

Recommended design principles:
- keep the first page simple and executive-friendly
- avoid too many visuals on one page
- use page titles that sound business-oriented
- keep metric naming consistent
- make segment analysis easy to compare visually
- use the summary CSVs for most visuals
- use the customer-level file mainly for drilldown or filtering

---

## 11. Portfolio presentation notes

When presenting this dashboard in the portfolio, emphasize that it is based on:
- a normalized MySQL schema
- SQL validation and experiment analysis
- reusable reporting views
- exported reporting datasets
- stakeholder-oriented dashboard design

This makes the dashboard more than just a BI exercise. It becomes the final layer of an end-to-end analytics workflow.