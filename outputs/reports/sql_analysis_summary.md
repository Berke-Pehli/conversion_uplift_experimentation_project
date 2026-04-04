# SQL Analysis Summary

## 1. Purpose

The SQL phase of this project was designed to validate the loaded Hillstrom experiment data, analyze campaign performance, and build reusable reporting views for downstream reporting and modeling.

The main business questions were:

- Are the treatment and control groups balanced?
- Do email campaigns outperform the control group?
- Which campaign performs best?
- Which customer segments respond more positively?
- How can the SQL layer support later reporting in Power BI and further modeling in Python?

---

## 2. Data Validation Summary

The SQL validation queries confirmed that the normalized MySQL schema was loaded correctly.

### Validation checks completed
- row counts across all tables
- duplicate primary key checks
- null checks in critical columns
- foreign key integrity checks
- binary value checks
- sanity checks on numeric columns
- sample full-schema joins

### Validation result
The validation phase showed that the database load was successful and structurally consistent.

Key confirmed points:
- lookup tables were populated correctly
- each customer appeared once in the customer and fact tables
- no major null or join integrity issues were detected
- binary flags remained valid after loading
- the full joined schema produced clean customer-level records

---

## 3. Experiment Group Balance

### Customer counts by campaign segment

| Segment | Campaign Type | Binary Treatment Flag | Customer Count |
|---|---|---:|---:|
| Womens E-Mail | womens_email | 1 | 21,387 |
| Mens E-Mail | mens_email | 1 | 21,307 |
| No E-Mail | control | 0 | 21,306 |

### Interpretation
The experiment groups are very well balanced. This supports meaningful comparison between treatment and control groups because the campaign populations are nearly equal in size.

---

## 4. Core KPI Summary by Campaign Segment

| Segment | Customer Count | Visit Rate | Conversion Rate | Avg Spend / Customer | Avg Spend / Converter | Total Spend |
|---|---:|---:|---:|---:|---:|---:|
| Mens E-Mail | 21,307 | 0.1828 | 0.0125 | 1.4226 | 113.5269 | 30,311.69 |
| No E-Mail | 21,306 | 0.1062 | 0.0057 | 0.6528 | 114.0027 | 13,908.33 |
| Womens E-Mail | 21,387 | 0.1514 | 0.0088 | 1.0772 | 121.8948 | 23,038.11 |

### Interpretation
Both email campaigns outperform the control group across the main top-line metrics.

The strongest overall campaign is **Mens E-Mail**, which has:
- the highest visit rate
- the highest conversion rate
- the highest average spend per customer
- the highest total spend

The **Womens E-Mail** campaign also beats control, but not as strongly as Mens E-Mail.

A notable nuance is that Womens E-Mail has the highest average spend per converter, which suggests that while it drives fewer conversions overall, converted customers in that group may spend more on average.

---

## 5. Treatment vs Control Summary

| Binary Treatment Flag | Customer Count | Visit Rate | Conversion Rate | Avg Spend / Customer | Total Spend |
|---|---:|---:|---:|---:|---:|
| 0 | 21,306 | 0.1062 | 0.0057 | 0.6528 | 13,908.33 |
| 1 | 42,694 | 0.1670 | 0.0107 | 1.2496 | 53,349.80 |

### Interpretation
Any email treatment performs better than the control group overall.

This suggests that sending an email campaign is beneficial on average. The next business question is no longer whether email should be sent at all, but rather:

- which customers should receive treatment
- and which campaign variant is more effective for different segments

This directly supports the later uplift modeling phase.

---

## 6. Uplift vs Control

| Segment | Visit Rate | Absolute Visit Uplift | Relative Visit Lift | Conversion Rate | Absolute Conversion Uplift | Relative Conversion Lift | Avg Spend / Customer | Absolute Spend Uplift |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Womens E-Mail | 0.1514 | 0.0452 | 0.425612 | 0.0088 | 0.0031 | 0.543860 | 1.077202 | 0.424413 |
| No E-Mail | 0.1062 | 0.0000 | 0.000000 | 0.0057 | 0.0000 | 0.000000 | 0.652789 | 0.000000 |
| Mens E-Mail | 0.1828 | 0.0766 | 0.721281 | 0.0125 | 0.0068 | 1.192982 | 1.422617 | 0.769828 |

### Interpretation
Both campaigns show positive uplift relative to control, but **Mens E-Mail** delivers the strongest incremental improvement.

Compared with the control group, Mens E-Mail produces:
- stronger visit uplift
- stronger conversion uplift
- stronger spend uplift

This is one of the most important findings of the SQL phase.

---

## 7. Segment-Level Findings

### 7.1 Channel-level findings
The channel-level summary suggests that **Multichannel** customers respond particularly well to treatment. Campaign performance is still positive for Web and Phone groups, but the strongest results appear in Multichannel and Web for some metrics.

This indicates that customer channel behavior may be an important segmentation variable for targeting.

### 7.2 Zip-code-level findings
The zip-code summary shows that **Rural** customers respond especially well to campaign treatment, particularly under the Mens E-Mail campaign.

This suggests geographic category may influence responsiveness and could be useful in later modeling and targeting strategies.

### 7.3 New vs existing customers
The `newbie` summary suggests that **existing customers** generally respond more strongly than newer customers, especially for visit rate and spend per customer.

This aligns with common CRM behavior where more established customers are easier to reactivate.

### 7.4 Merchandise affinity
The merchandise-affinity breakdown shows particularly strong results among customers with stronger prior merchandise engagement. In the subset where both `mens = 1` and `womens = 1`, the Mens E-Mail campaign performs very strongly.

This suggests that prior category affinity is likely an important predictor of treatment response.

### 7.5 History segment
The history-segment summary shows that customers with stronger historical value generally produce stronger campaign outcomes. Higher-spend history groups show higher visit, conversion, and spend outcomes than lower-spend groups.

This supports the idea that customer value history should play an important role in targeting decisions.

---

## 8. Main Business Insights

The SQL analysis suggests the following:

1. The experiment is balanced and structurally reliable for comparison.
2. Any email treatment outperforms no email overall.
3. **Mens E-Mail** is the strongest aggregate campaign.
4. Campaign effectiveness is not uniform across all customers.
5. Response appears to vary by:
   - channel
   - zip-code group
   - new vs existing customer status
   - merchandise affinity
   - customer history segment
6. Higher-value and more engaged segments appear especially responsive.

---

## 9. Recommendations Based on SQL Alone

Based on the SQL findings alone, a business team could reasonably consider:

- continuing email treatment rather than using a no-email strategy
- favoring **Mens E-Mail** as the stronger overall campaign
- prioritizing more responsive customer groups such as:
  - higher-history customers
  - multichannel users
  - some rural segments
  - higher-merchandise-affinity customers
- avoiding a one-size-fits-all campaign strategy

These are still aggregate findings. A more precise treatment strategy requires customer-level predictive and uplift modeling.

---

## 10. Reporting View Layer

To make the SQL output reusable, the project also includes reporting views such as:

- `vw_customer_experiment_detail`
- `vw_campaign_summary`
- `vw_treatment_control_summary`
- `vw_segment_uplift_summary`
- `vw_channel_campaign_summary`
- `vw_zip_campaign_summary`
- `vw_newbie_campaign_summary`
- `vw_history_segment_campaign_summary`

These views provide a cleaner reporting layer for:
- SQL exploration
- Power BI exports
- Python extraction
- project documentation

---

## 11. Next Analytical Step

The SQL phase answers the main aggregate business questions, but it does not yet tell us which **individual customers** should receive treatment.

The next step is to use Python modeling to compare:
- standard conversion prediction models
- uplift-oriented approaches

This will extend the analysis from aggregate performance into customer-level targeting strategy.