# CLAUDE.md — Pricing Hold Analyzer for NVIDIA Job Application

## CONTEXT

This project is a **portfolio piece** being built by Arnaud Chacon as part of a job application for the **Pricing Analyst** role in NVIDIA's WWFO (Worldwide Field Operations) Pricing team in Hong Kong.

The JD specifically says: "Analyzing pricing hold reasons, durations, root causes, and trends; developing and implementing solutions to minimize hold times." This tool does exactly that.

Arnaud's background:
- Worked at Payplug (French payments fintech, BPCE Group) doing sales ops, pricing data management, dashboards, CRM management, automation
- Currently at NATO doing finance operations in SAP and Oracle ERP — 80-120 transactions/day
- Audit background reviewing financial data for 15+ corporate clients
- Skills: Python, Excel (VBA), SQL, Google Apps Script, Zapier, Streamlit

---

## WHAT TO BUILD

A **Streamlit web app** called **"PriceOps Analyzer"** — an interactive Pricing Hold Analysis Dashboard that helps a pricing operations team understand why sales orders get stuck, how long they stay stuck, and what to fix.

---

## CORE FUNCTIONALITY

### 1. Demo Mode (default on load)
- Pre-loaded with realistic sample data — no upload required
- Sample data simulates a semiconductor/GPU company's APAC sales operations
- User sees the full dashboard immediately on first load
- This is critical: the hiring manager will click the link and judge it in 30 seconds

### 2. Upload Mode
- User can upload their own sales order data (CSV)
- App processes it through the same analysis engine
- Show expected CSV format with a downloadable template

### 3. Dashboard Views

#### A. Executive Summary (top of page)
Four metric cards:
- **Total Orders on Hold:** count of orders currently in hold status
- **Average Hold Duration:** in hours, with trend arrow (up/down vs previous period)
- **Resolution Rate:** % of holds resolved within SLA (e.g., 24 hours)
- **Top Hold Reason:** most frequent reason with count

#### B. Hold Reason Analysis
- **Donut/pie chart:** distribution of hold reasons (e.g., "Missing Price List", "Expired Quote", "Discount Approval Pending", "Customer Master Data Incomplete", "Currency Mismatch", "Regional Price Override Required")
- **Bar chart:** hold count by reason, sorted descending
- **Table:** hold reasons with average duration, count, % of total, trend vs previous month

#### C. Duration Analysis
- **Histogram:** distribution of hold durations (0-4h, 4-8h, 8-24h, 24-48h, 48h+)
- **Box plot or violin plot:** hold duration by reason category — shows which problems take longest to fix
- **Line chart:** average hold duration over time (daily/weekly trend) — shows if things are getting better or worse
- **SLA breach rate:** % of holds exceeding 24h target, broken by reason

#### D. Root Cause Deep Dive
- **Sankey diagram or tree map:** Hold Reason → Root Cause → Resolution Action flow
- **Pareto chart:** 80/20 analysis showing which 20% of root causes drive 80% of hold time
- **Table:** root causes ranked by total hold hours (not just count — a rare issue that takes 3 days to resolve is worse than a common one resolved in 1 hour)

#### E. Business Unit & Region View
- **Heatmap:** hold frequency by Business Unit × Region (APAC, EMEA, Americas)
- **Bar chart:** hold duration by region — shows where the bottlenecks are geographically
- **Table:** BU breakdown with hold count, avg duration, SLA breach rate

#### F. Trends & Forecasting
- **Line chart:** weekly hold volume and avg duration over 3 months
- **Highlight:** week-over-week changes, flag if trending up
- **Simple forecast:** if current trend continues, projected hold volume next month (use basic linear regression or moving average)

#### G. Recommendations Engine (this is the wow factor)
Based on the data analysis, auto-generate actionable recommendations:
- "Missing Price List accounts for 34% of all holds and averages 18h resolution. Recommendation: implement automated price list sync from BU systems to reduce manual updates."
- "APAC region has 2.3x higher hold rate than Americas. Root cause: timezone delay in discount approvals. Recommendation: delegate approval authority to regional pricing leads."
- "Expired quotes caused 45 holds this month, up 60% from last month. Recommendation: implement automated quote expiry alerts 7 days before expiration."

These should be generated dynamically based on the actual data patterns — not hardcoded.

### 4. Export
- Download full hold analysis report as CSV
- Download executive summary as PDF (if feasible, otherwise CSV is fine)

---

## SAMPLE DATA SPECIFICATION

### File: sales_order_holds.csv

**Columns:**
- `order_id` — e.g., "SO-2026-HK-00142", "SO-2026-US-00891"
- `order_date` — date the order was placed
- `hold_start` — datetime when hold was triggered
- `hold_end` — datetime when hold was resolved (null if still open)
- `hold_duration_hours` — calculated field
- `hold_status` — "Resolved", "Open", "Escalated"
- `hold_reason` — categorical (see below)
- `root_cause` — more specific than reason (see below)
- `resolution_action` — what was done to fix it (see below)
- `business_unit` — "Gaming", "Data Center", "Professional Visualization", "Automotive", "OEM"
- `region` — "APAC", "EMEA", "Americas"
- `sub_region` — "Hong Kong", "Japan", "Korea", "Singapore", "India", "Australia", "Germany", "UK", "France", "US West", "US East", "Canada", "Brazil"
- `customer_name` — realistic names (see below)
- `product_line` — "GeForce RTX", "Quadro", "Tesla/A100", "DRIVE", "DGX", "HGX", "Jetson"
- `currency` — "USD", "HKD", "EUR", "JPY", "KRW", "SGD", "INR", "GBP"
- `order_value` — in local currency
- `sales_rep` — name
- `priority` — "Standard", "Urgent", "Critical"

### Hold Reasons (and their root causes):

**1. Missing Price List (most common, ~25%)**
- Root causes: "BU price list not uploaded", "New product not in system", "Price list version expired"
- Avg resolution: 8-16 hours
- Resolution: "Price list uploaded by BU team", "Manual price entry", "Escalated to product management"

**2. Discount Approval Pending (~20%)**
- Root causes: "Discount exceeds threshold", "Non-standard deal structure", "Approver out of office"
- Avg resolution: 12-36 hours (long because of approval chains)
- Resolution: "Approved by regional manager", "Rejected — repriced", "Auto-approved after escalation"

**3. Customer Master Data Incomplete (~18%)**
- Root causes: "Missing billing address", "Tax ID not on file", "Credit check pending", "New customer not set up in SAP"
- Avg resolution: 4-12 hours
- Resolution: "Customer data updated", "Credit approved", "Customer contacted for info"

**4. Currency/FX Mismatch (~12%)**
- Root causes: "Order currency differs from price list", "FX rate expired", "Multi-currency order"
- Avg resolution: 2-6 hours
- Resolution: "Currency corrected", "FX rate updated", "Manual override applied"

**5. Regional Price Override Required (~10%)**
- Root causes: "Country-specific pricing not configured", "Competitive bid requires special pricing", "Government/education discount"
- Avg resolution: 16-48 hours (needs regional approval)
- Resolution: "Regional price approved", "Standard pricing applied", "Escalated to HQ"

**6. Expired Quote (~8%)**
- Root causes: "Quote validity exceeded", "Customer delayed PO", "Price increase since quote"
- Avg resolution: 8-24 hours
- Resolution: "Quote reissued", "Original price honored", "New quote with updated pricing"

**7. System Error (~7%)**
- Root causes: "SAP pricing condition error", "Duplicate order entry", "Interface sync failure"
- Avg resolution: 2-8 hours
- Resolution: "SAP config corrected", "Duplicate removed", "Manual reprocessing"

### Customer Names (realistic NVIDIA channel partners/customers):

**APAC:**
- Lenovo Hong Kong Ltd
- ASUS Computer HK
- Dell Technologies Japan
- Samsung Electronics Korea
- Supermicro Singapore
- Tata Consultancy Services India
- Fujitsu Australia
- Gigabyte Technology Taiwan
- MSI Computer Hong Kong
- NEC Corporation Japan

**EMEA:**
- BMW Group Germany
- Siemens Digital Industries
- Bosch Automotive EMEA
- Mercedes-Benz AG
- CERN Switzerland
- Dassault Systèmes France
- BAE Systems UK
- Volkswagen Group

**Americas:**
- Amazon Web Services
- Microsoft Azure
- Meta Platforms Inc
- Tesla Inc
- General Motors
- Lockheed Martin
- Johns Hopkins University
- Stanford University

### Data Volume:
- Generate **500 orders** spanning October 2025 — January 2026
- ~70% resolved, ~20% open, ~10% escalated
- Make sure patterns are realistic:
  - APAC has higher "Currency Mismatch" and "Regional Price Override" rates
  - Americas has more "Discount Approval Pending" (bigger deals)
  - "Missing Price List" spikes in November (new product launches)
  - Hold durations trend slightly downward over time (showing improvement)
  - A few outlier orders with 72+ hour holds (critical issues)

---

## UI / DESIGN

### Colour Scheme (NVIDIA-inspired):
- Primary: `#76B900` (NVIDIA green)
- Secondary: `#1A1A1A` (near-black)
- Background: `#FAFAFA` (light grey)
- Cards: `#FFFFFF` with subtle shadow
- Accent dark: `#2D2D2D`
- Success/Resolved: `#22C55E` (green)
- Warning/Open: `#F59E0B` (amber)
- Error/Escalated/SLA Breach: `#EF4444` (red)
- Text: `#1A1A1A`
- Muted text: `#6B7280`
- Chart palette: `#76B900`, `#F59E0B`, `#EF4444`, `#3B82F6`, `#8B5CF6`, `#EC4899`

### Layout:
```
┌──────────────────────────────────────────────┐
│  📊 PriceOps Analyzer                        │
│  Pricing Hold Analysis Dashboard             │
│  Built by Arnaud Chacon                       │
├──────────────────────────────────────────────┤
│  [Demo Mode] [Upload Your Data]              │
├──────────────────────────────────────────────┤
│                                              │
│  ┌─────────┐ ┌─────────┐ ┌────────┐ ┌─────┐ │
│  │Orders on│ │Avg Hold │ │Resolut.│ │ Top │ │
│  │  Hold   │ │Duration │ │  Rate  │ │Reason│ │
│  │  127    │ │ 14.2h   │ │  78%   │ │Miss.│ │
│  │         │ │ ↓ -2.1h │ │ ↑ +3%  │ │Price│ │
│  └─────────┘ └─────────┘ └────────┘ └─────┘ │
│                                              │
│  TABS:                                       │
│  [Hold Reasons] [Duration Analysis]          │
│  [Root Causes] [By Region/BU]               │
│  [Trends] [Recommendations] [Export]        │
│                                              │
└──────────────────────────────────────────────┘
```

### Streamlit Styling:
- Use `st.markdown()` with custom CSS for NVIDIA green accent
- Override default Streamlit blue with `#76B900`
- Use `plotly` for all charts (interactive, hover details, professional)
- Use `st.tabs()` for the different analysis views
- Use `st.metric()` with delta for the summary cards

---

## TECH STACK

- **Streamlit** — main framework
- **Pandas** — data processing
- **Plotly** — charts (all interactive)
- **NumPy** — calculations
- **Python** — core analysis engine

### Dependencies (requirements.txt):
```
streamlit
pandas
plotly
numpy
openpyxl
```

---

## FILE STRUCTURE

```
pricing-hold-analyzer/
├── app.py                    # Main Streamlit app
├── analysis_engine.py        # Core analysis logic
├── recommendations.py        # Auto-generated recommendations engine
├── sample_data.py            # Generate realistic sample data
├── styles.py                 # Custom CSS and NVIDIA colour constants
├── requirements.txt          # Dependencies
├── README.md                 # Project description
├── data/
│   └── sample_orders.csv     # Pre-generated sample data
└── CLAUDE.md                 # This file
```

---

## RECOMMENDATIONS ENGINE LOGIC (recommendations.py)

This is what makes the tool special. It should analyse the data and generate specific, actionable recommendations — not generic advice.

```python
# Pseudocode:

def generate_recommendations(df):
    recommendations = []
    
    # Rule 1: Top hold reason by volume
    top_reason = get_most_frequent_hold_reason(df)
    top_reason_pct = get_percentage(top_reason)
    top_reason_avg_hours = get_avg_duration(top_reason)
    recommendations.append({
        "priority": "HIGH",
        "finding": f"{top_reason} accounts for {top_reason_pct}% of all holds",
        "impact": f"Average resolution time: {top_reason_avg_hours}h",
        "recommendation": generate_specific_recommendation(top_reason)
    })
    
    # Rule 2: Region with highest hold rate
    worst_region = get_region_with_highest_hold_rate(df)
    region_vs_avg = compare_to_average(worst_region)
    recommendations.append({...})
    
    # Rule 3: SLA breach trend
    if sla_breach_rate_increasing(df):
        recommendations.append({
            "priority": "CRITICAL",
            "finding": "SLA breach rate increased X% month-over-month",
            "recommendation": "..."
        })
    
    # Rule 4: Approval bottlenecks
    if avg_approval_time > threshold:
        recommendations.append({...})
    
    # Rule 5: Pareto — which 20% of root causes drive 80% of hold hours
    pareto_causes = get_pareto_root_causes(df)
    recommendations.append({...})
    
    # Rule 6: New product launch impact
    if new_product_holds_spike(df):
        recommendations.append({...})
    
    # Rule 7: Repeat offenders — customers with recurring holds
    repeat_customers = get_customers_with_most_holds(df)
    recommendations.append({...})
    
    return sorted(recommendations, by="priority")
```

Display recommendations as cards with priority colour coding (red/amber/green), clear finding → impact → recommendation structure, and an estimated time/cost savings if the recommendation is implemented.

---

## README.md CONTENT

```markdown
# PriceOps Analyzer — Pricing Hold Analysis Dashboard

An interactive dashboard for analyzing pricing holds on sales orders. Built to help 
pricing operations teams understand why orders get stuck, how long they stay stuck, 
and what to fix first.

## Features
- **Hold Reason Analysis** with distribution, frequency, and duration breakdown
- **Root Cause Deep Dive** with Pareto analysis and resolution tracking
- **Duration Analysis** with SLA monitoring and trend detection
- **Region & Business Unit** heatmaps and comparative views
- **Trend Forecasting** with week-over-week change tracking
- **AI-powered Recommendations** that auto-generate actionable insights from the data
- **Demo mode** with realistic semiconductor industry sample data
- **Upload mode** for your own sales order data

## Why I Built This
I built this tool as part of my application for the Pricing Analyst role at NVIDIA's 
WWFO Pricing team. The JD specifically mentions "analyzing pricing hold reasons, 
durations, root causes, and trends" — so I built a tool that does exactly that.

## Tech Stack
- Python, Streamlit, Pandas, Plotly

## About Me
Arnaud Chacon — Sales Operations & Pricing Analyst with experience in fintech 
(Payplug/BPCE Group) and finance operations (NATO). Strong SAP/Oracle, Excel, 
and Python background.
- LinkedIn: [link]
- Email: arnaudchacon@gmail.com

## How to Run
```bash
pip install -r requirements.txt
streamlit run app.py
```
```

---

## IMPORTANT NOTES FOR CLAUDE

1. **The Recommendations Engine is the differentiator.** Any analyst can build a dashboard. The recommendations show strategic thinking — the ability to look at data and say "here's what we should do about it." This is what separates a pricing analyst from a data entry person. Make these recommendations smart, specific, and data-driven.

2. **Use NVIDIA's actual product lines.** GeForce RTX, Quadro, Tesla/A100, DGX, HGX, DRIVE, Jetson — these are real NVIDIA products. Using them shows the candidate understands the company. Don't use generic "Product A, Product B."

3. **The Pareto analysis is crucial.** Pricing teams live by 80/20. Showing which 20% of root causes create 80% of hold time is exactly how a pricing operations person thinks. Make this chart prominent and clear.

4. **Hold durations should feel realistic.** A missing price list taking 8-16h is realistic (need to wait for the BU team in another timezone). A currency mismatch taking 2-6h is realistic (quick fix once identified). An approval chain taking 24-48h is realistic (multiple levels). Don't make everything resolve in 1 hour — that's not how it works.

5. **APAC focus in the sample data.** The role is based in Hong Kong. Make sure ~40% of sample orders are APAC, with realistic APAC customers, currencies (HKD, JPY, KRW, SGD, INR), and timezone-related hold patterns (e.g., approvals delayed because US HQ is asleep).

6. **The SLA concept is important.** Define an SLA (e.g., 24h resolution target) and track breach rates. This shows the candidate understands operational KPIs and accountability.

7. **Make the demo data tell a story.** The data should show: hold volume trending slightly down over 4 months (improvement), but one category (e.g., "Regional Price Override") trending up (problem area). This gives the recommendations engine something interesting to flag.

8. **Keep it fast.** 500 orders is enough to demonstrate the concept. The app should load in under 3 seconds.

9. **NVIDIA green (#76B900) is the signature.** Use it for the primary accent, chart highlights, and the header. But don't overdo it — the dashboard should look professional, not like a gaming website.

10. **Footer:** "Built by Arnaud Chacon as a demonstration project for NVIDIA's WWFO Pricing team. Data is synthetically generated for illustration purposes."
