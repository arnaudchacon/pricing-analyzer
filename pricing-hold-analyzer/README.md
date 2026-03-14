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
- **Smart Recommendations Engine** that auto-generates actionable insights from the data
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
- Email: arnaudchacon@gmail.com

## How to Run
```bash
pip install -r requirements.txt
streamlit run app.py
```
