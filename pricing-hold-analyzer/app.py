"""
PriceOps Analyzer — Pricing Hold Analysis Dashboard
Built by Arnaud Chacon for NVIDIA WWFO Pricing team application.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import io

from sample_data import generate_sample_data, save_sample_csv
from analysis_engine import (
    compute_executive_summary,
    hold_reason_breakdown,
    duration_analysis,
    root_cause_analysis,
    region_bu_analysis,
    trend_analysis,
)
from recommendations import generate_recommendations
from styles import (
    get_custom_css,
    get_plotly_layout,
    CHART_COLORS,
    PRIORITY_COLORS,
    STATUS_COLORS,
    NVIDIA_GREEN,
    NVIDIA_GREEN_LIGHT,
    NVIDIA_BLACK,
    NVIDIA_GRAY_950,
    NVIDIA_GRAY_900,
    NVIDIA_GRAY_800,
    NVIDIA_WHITE,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    TEXT_MUTED,
    CARD_BG,
    CARD_BORDER,
    ERROR,
    WARNING,
    SUCCESS,
    INFO,
)

# --- Page Config ---
st.set_page_config(
    page_title="PriceOps Analyzer | NVIDIA Pricing Hold Dashboard",
    page_icon="https://www.nvidia.com/favicon.ico",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --- Apply custom CSS ---
st.markdown(get_custom_css(), unsafe_allow_html=True)


# --- Data Loading ---
@st.cache_data
def load_demo_data():
    df = generate_sample_data(n_orders=500, seed=42)
    return df


def parse_uploaded_data(uploaded_file):
    try:
        df = pd.read_csv(uploaded_file)
        df["order_date"] = pd.to_datetime(df["order_date"])
        df["hold_start"] = pd.to_datetime(df["hold_start"])
        df["hold_end"] = pd.to_datetime(df["hold_end"], errors="coerce")
        return df, None
    except Exception as e:
        return None, str(e)


# --- Header ---
st.markdown(
    """
    <div class="nvidia-header">
        <h1><span>PriceOps</span> Analyzer</h1>
        <p>Pricing Hold Analysis Dashboard &nbsp;|&nbsp; Built by Arnaud Chacon</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# --- Mode Selection ---
col_mode1, col_mode2, col_mode3 = st.columns([1, 1, 4])
with col_mode1:
    demo_mode = st.button("Demo Mode", type="primary", use_container_width=True)
with col_mode2:
    upload_mode = st.button("Upload Your Data", use_container_width=True)

# Session state for mode
if "mode" not in st.session_state:
    st.session_state.mode = "demo"
if demo_mode:
    st.session_state.mode = "demo"
if upload_mode:
    st.session_state.mode = "upload"

# --- Load Data ---
df = None
if st.session_state.mode == "demo":
    df = load_demo_data()
else:
    st.markdown(f'<p style="color:{TEXT_SECONDARY}; margin-top:12px;">Upload a CSV file with the expected columns. <a href="#" style="color:{NVIDIA_GREEN};">Download template</a></p>', unsafe_allow_html=True)
    uploaded = st.file_uploader("Upload sales order data (CSV)", type=["csv"], label_visibility="collapsed")
    if uploaded:
        df, err = parse_uploaded_data(uploaded)
        if err:
            st.error(f"Error parsing file: {err}")
    else:
        # Show template columns
        st.markdown(f"""
        <div style="background:{CARD_BG}; border:1px solid {CARD_BORDER}; border-radius:8px; padding:20px; margin-top:12px;">
            <p style="color:{TEXT_PRIMARY}; font-weight:600; margin-bottom:8px;">Expected CSV columns:</p>
            <p style="color:{TEXT_SECONDARY}; font-size:13px; font-family:monospace;">
            order_id, order_date, hold_start, hold_end, hold_duration_hours, hold_status,
            hold_reason, root_cause, resolution_action, business_unit, region, sub_region,
            customer_name, product_line, currency, order_value, sales_rep, priority
            </p>
        </div>
        """, unsafe_allow_html=True)
        # Offer demo data download
        demo_df = load_demo_data()
        csv_buf = io.StringIO()
        demo_df.to_csv(csv_buf, index=False)
        st.download_button("Download Template CSV", csv_buf.getvalue(), "sample_orders_template.csv", "text/csv")
        st.stop()

if df is None:
    st.stop()

# --- Executive Summary ---
summary = compute_executive_summary(df)

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Orders on Hold", summary["total_on_hold"], delta=None)
with c2:
    st.metric(
        "Avg Hold Duration",
        f'{summary["avg_duration"]}h',
        delta=f'{summary["duration_delta"]:+.1f}h vs prev period',
        delta_color="inverse",
    )
with c3:
    st.metric(
        "SLA Resolution Rate",
        f'{summary["resolution_rate"]}%',
        delta=f'{summary["rate_delta"]:+.1f}pp vs prev period',
    )
with c4:
    st.metric(
        "Top Hold Reason",
        summary["top_reason"],
        delta=f'{summary["top_reason_count"]} orders',
        delta_color="off",
    )

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

# --- Tabs ---
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "Hold Reasons",
    "Duration Analysis",
    "Root Causes",
    "Region & BU",
    "Trends",
    "Recommendations",
    "Export",
])

# ============================================================
# TAB 1: Hold Reasons
# ============================================================
with tab1:
    reason_data = hold_reason_breakdown(df)

    col_a, col_b = st.columns(2)

    with col_a:
        # Donut chart
        fig_donut = go.Figure(go.Pie(
            labels=reason_data["hold_reason"],
            values=reason_data["count"],
            hole=0.55,
            marker=dict(colors=CHART_COLORS[:len(reason_data)]),
            textinfo="label+percent",
            textfont=dict(size=12, color=TEXT_PRIMARY),
            hovertemplate="<b>%{label}</b><br>Count: %{value}<br>%{percent}<extra></extra>",
        ))
        layout = get_plotly_layout("Hold Reason Distribution", height=420)
        layout["showlegend"] = False
        fig_donut.update_layout(**layout)
        # Center annotation
        fig_donut.add_annotation(
            text=f"<b>{summary['total_orders']}</b><br><span style='font-size:11px;color:{TEXT_MUTED}'>Total Orders</span>",
            showarrow=False, font=dict(size=22, color=TEXT_PRIMARY),
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    with col_b:
        # Bar chart
        fig_bar = go.Figure(go.Bar(
            x=reason_data["count"],
            y=reason_data["hold_reason"],
            orientation="h",
            marker=dict(color=NVIDIA_GREEN, line=dict(width=0)),
            text=reason_data["count"],
            textposition="outside",
            textfont=dict(color=TEXT_PRIMARY, size=12),
            hovertemplate="<b>%{y}</b><br>Count: %{x}<br>Avg: %{customdata[0]}h<extra></extra>",
            customdata=reason_data[["avg_duration"]].values,
        ))
        layout = get_plotly_layout("Hold Count by Reason", height=420)
        layout["yaxis"]["autorange"] = "reversed"
        layout["xaxis"]["showgrid"] = False
        fig_bar.update_layout(**layout)
        st.plotly_chart(fig_bar, use_container_width=True)

    # Table
    st.markdown(f'<div class="section-header">Detailed Breakdown</div>', unsafe_allow_html=True)
    display_df = reason_data[["hold_reason", "count", "pct_of_total", "avg_duration", "median_duration", "total_hours", "mom_trend_pct"]].copy()
    display_df.columns = ["Hold Reason", "Count", "% of Total", "Avg Duration (h)", "Median (h)", "Total Hours", "MoM Trend %"]
    st.dataframe(display_df, use_container_width=True, hide_index=True)


# ============================================================
# TAB 2: Duration Analysis
# ============================================================
with tab2:
    dur_data = duration_analysis(df)

    col_d1, col_d2 = st.columns(2)

    with col_d1:
        # Histogram
        fig_hist = go.Figure(go.Bar(
            x=dur_data["histogram"].index.tolist(),
            y=dur_data["histogram"].values,
            marker=dict(
                color=[NVIDIA_GREEN, CHART_COLORS[1], CHART_COLORS[2], WARNING, ERROR],
            ),
            text=dur_data["histogram"].values.astype(int),
            textposition="outside",
            textfont=dict(color=TEXT_PRIMARY),
            hovertemplate="<b>%{x}</b><br>Orders: %{y}<extra></extra>",
        ))
        layout = get_plotly_layout("Hold Duration Distribution", height=400)
        layout["xaxis"]["title"] = "Duration Bucket"
        layout["yaxis"]["title"] = "Number of Orders"
        fig_hist.update_layout(**layout)
        st.plotly_chart(fig_hist, use_container_width=True)

    with col_d2:
        # Box plot by reason
        fig_box = go.Figure()
        reasons_sorted = df.groupby("hold_reason")["hold_duration_hours"].median().sort_values(ascending=False).index
        for i, reason in enumerate(reasons_sorted):
            subset = df[df["hold_reason"] == reason]
            fig_box.add_trace(go.Box(
                y=subset["hold_duration_hours"],
                name=reason.replace(" ", "<br>") if len(reason) > 15 else reason,
                marker_color=CHART_COLORS[i % len(CHART_COLORS)],
                line=dict(color=CHART_COLORS[i % len(CHART_COLORS)]),
                boxmean=True,
            ))
        layout = get_plotly_layout("Duration by Hold Reason", height=400)
        layout["showlegend"] = False
        layout["yaxis"]["title"] = "Hours"
        fig_box.update_layout(**layout)
        st.plotly_chart(fig_box, use_container_width=True)

    # Daily trend
    fig_trend = go.Figure()
    daily = dur_data["daily_trend"]
    fig_trend.add_trace(go.Scatter(
        x=daily["date"], y=daily["avg_duration"],
        mode="lines+markers",
        line=dict(color=NVIDIA_GREEN, width=2),
        marker=dict(size=4, color=NVIDIA_GREEN),
        hovertemplate="<b>%{x|%b %d}</b><br>Avg: %{y:.1f}h<extra></extra>",
    ))
    # Add 24h SLA line
    fig_trend.add_hline(y=24, line_dash="dash", line_color=ERROR, opacity=0.7,
                         annotation_text="24h SLA Target", annotation_font_color=ERROR)
    layout = get_plotly_layout("Average Hold Duration Over Time", height=350)
    layout["xaxis"]["title"] = ""
    layout["yaxis"]["title"] = "Avg Duration (hours)"
    fig_trend.update_layout(**layout)
    st.plotly_chart(fig_trend, use_container_width=True)

    # SLA breach table
    st.markdown(f'<div class="section-header">SLA Breach Rate by Reason</div>', unsafe_allow_html=True)
    breach = dur_data["breach_by_reason"].copy()
    breach.columns = ["Hold Reason", "SLA Breach %"]
    st.dataframe(breach, use_container_width=True, hide_index=True)


# ============================================================
# TAB 3: Root Causes
# ============================================================
with tab3:
    rc_data = root_cause_analysis(df)

    # Pareto chart
    pareto = rc_data["pareto"].head(15)
    fig_pareto = make_subplots(specs=[[{"secondary_y": True}]])
    fig_pareto.add_trace(
        go.Bar(
            x=pareto["root_cause"], y=pareto["total_hours"],
            marker=dict(color=NVIDIA_GREEN),
            name="Total Hold Hours",
            text=pareto["total_hours"].astype(int),
            textposition="outside",
            textfont=dict(color=TEXT_PRIMARY, size=10),
            hovertemplate="<b>%{x}</b><br>Total: %{y:,.0f}h<br>Avg: %{customdata[0]}h<br>Count: %{customdata[1]}<extra></extra>",
            customdata=pareto[["avg_duration", "count"]].values,
        ),
        secondary_y=False,
    )
    fig_pareto.add_trace(
        go.Scatter(
            x=pareto["root_cause"], y=pareto["cumulative_pct"],
            mode="lines+markers",
            line=dict(color=WARNING, width=2.5),
            marker=dict(size=7, color=WARNING),
            name="Cumulative %",
            hovertemplate="%{y:.1f}%<extra></extra>",
        ),
        secondary_y=True,
    )
    # 80% line
    fig_pareto.add_hline(y=80, line_dash="dash", line_color=ERROR, opacity=0.6,
                          secondary_y=True, annotation_text="80% threshold",
                          annotation_font_color=ERROR)
    layout = get_plotly_layout("Root Cause Pareto — 80/20 Analysis", height=480)
    fig_pareto.update_layout(**layout)
    fig_pareto.update_layout(
        yaxis=dict(title="Total Hold Hours", gridcolor=NVIDIA_GRAY_800, tickfont=dict(color=TEXT_SECONDARY)),
        yaxis2=dict(title="Cumulative %", gridcolor="rgba(0,0,0,0)", tickfont=dict(color=TEXT_SECONDARY), range=[0, 105]),
        xaxis=dict(tickangle=-35, tickfont=dict(size=10, color=TEXT_SECONDARY)),
        legend=dict(orientation="h", y=1.12, font=dict(color=TEXT_SECONDARY)),
    )
    st.plotly_chart(fig_pareto, use_container_width=True)

    # Sankey: reason -> root cause -> resolution
    flow = rc_data["flow"]
    if len(flow) > 0:
        st.markdown(f'<div class="section-header">Hold Resolution Flow</div>', unsafe_allow_html=True)

        all_labels = list(pd.concat([flow["hold_reason"], flow["root_cause"], flow["resolution_action"]]).unique())
        label_idx = {label: i for i, label in enumerate(all_labels)}

        n_reasons = flow["hold_reason"].nunique()
        n_causes = flow["root_cause"].nunique()
        n_resolutions = flow["resolution_action"].nunique()
        node_colors = (
            [NVIDIA_GREEN] * n_reasons
            + [CHART_COLORS[1]] * n_causes
            + [CHART_COLORS[2]] * n_resolutions
        )
        # Pad if needed
        while len(node_colors) < len(all_labels):
            node_colors.append(CHART_COLORS[3])

        fig_sankey = go.Figure(go.Sankey(
            node=dict(
                pad=15, thickness=20,
                label=all_labels,
                color=node_colors[:len(all_labels)],
                line=dict(width=0),
            ),
            link=dict(
                source=[label_idx[r] for r in flow["hold_reason"]] + [label_idx[r] for r in flow["root_cause"]],
                target=[label_idx[r] for r in flow["root_cause"]] + [label_idx[r] for r in flow["resolution_action"]],
                value=list(flow["count"]) + list(flow["count"]),
                color=f"rgba(118, 185, 0, 0.15)",
            ),
        ))
        layout = get_plotly_layout("", height=500)
        fig_sankey.update_layout(**layout)
        st.plotly_chart(fig_sankey, use_container_width=True)

    # Root cause table
    st.markdown(f'<div class="section-header">Root Causes Ranked by Total Hold Hours</div>', unsafe_allow_html=True)
    rc_table = rc_data["pareto"][["root_cause", "count", "total_hours", "avg_duration", "cumulative_pct"]].copy()
    rc_table.columns = ["Root Cause", "Count", "Total Hours", "Avg Duration (h)", "Cumulative %"]
    st.dataframe(rc_table, use_container_width=True, hide_index=True)


# ============================================================
# TAB 4: Region & BU
# ============================================================
with tab4:
    rbu = region_bu_analysis(df)

    col_r1, col_r2 = st.columns(2)

    with col_r1:
        # Heatmap: count
        hm = rbu["heatmap_count"]
        fig_hm = go.Figure(go.Heatmap(
            z=hm.values,
            x=hm.columns.tolist(),
            y=hm.index.tolist(),
            colorscale=[[0, NVIDIA_GRAY_900], [0.5, "#3F8500"], [1, NVIDIA_GREEN]],
            text=hm.values,
            texttemplate="%{text}",
            textfont=dict(size=14, color=TEXT_PRIMARY),
            hovertemplate="<b>%{y}</b> × <b>%{x}</b><br>Holds: %{z}<extra></extra>",
            colorbar=dict(tickfont=dict(color=TEXT_SECONDARY)),
        ))
        layout = get_plotly_layout("Hold Frequency: BU × Region", height=380)
        fig_hm.update_layout(**layout)
        st.plotly_chart(fig_hm, use_container_width=True)

    with col_r2:
        # Heatmap: duration
        hm_dur = rbu["heatmap_duration"]
        fig_hm2 = go.Figure(go.Heatmap(
            z=hm_dur.values,
            x=hm_dur.columns.tolist(),
            y=hm_dur.index.tolist(),
            colorscale=[[0, NVIDIA_GRAY_900], [0.5, "#DF6500"], [1, ERROR]],
            text=hm_dur.values,
            texttemplate="%{text:.1f}h",
            textfont=dict(size=13, color=TEXT_PRIMARY),
            hovertemplate="<b>%{y}</b> × <b>%{x}</b><br>Avg Duration: %{z:.1f}h<extra></extra>",
            colorbar=dict(tickfont=dict(color=TEXT_SECONDARY)),
        ))
        layout = get_plotly_layout("Avg Hold Duration: BU × Region", height=380)
        fig_hm2.update_layout(**layout)
        st.plotly_chart(fig_hm2, use_container_width=True)

    # Region bar chart
    region_stats = rbu["region_stats"]
    fig_region = go.Figure()
    fig_region.add_trace(go.Bar(
        x=region_stats["region"],
        y=region_stats["avg_duration"],
        marker=dict(color=[CHART_COLORS[i] for i in range(len(region_stats))]),
        text=[f"{v:.1f}h" for v in region_stats["avg_duration"]],
        textposition="outside",
        textfont=dict(color=TEXT_PRIMARY, size=13),
        hovertemplate="<b>%{x}</b><br>Avg Duration: %{y:.1f}h<br>Total Orders: %{customdata[0]}<extra></extra>",
        customdata=region_stats[["count"]].values,
    ))
    layout = get_plotly_layout("Average Hold Duration by Region", height=350)
    layout["yaxis"]["title"] = "Avg Duration (hours)"
    fig_region.update_layout(**layout)
    st.plotly_chart(fig_region, use_container_width=True)

    # BU table
    st.markdown(f'<div class="section-header">Business Unit Breakdown</div>', unsafe_allow_html=True)
    bu_table = rbu["bu_stats"][["business_unit", "count", "avg_duration", "total_hours", "sla_breach_pct"]].copy()
    bu_table.columns = ["Business Unit", "Hold Count", "Avg Duration (h)", "Total Hours", "SLA Breach %"]
    bu_table["Total Hours"] = bu_table["Total Hours"].round(0)
    st.dataframe(bu_table, use_container_width=True, hide_index=True)


# ============================================================
# TAB 5: Trends
# ============================================================
with tab5:
    trends = trend_analysis(df)
    weekly = trends["weekly"]

    # Dual axis: volume + duration
    fig_trends = make_subplots(specs=[[{"secondary_y": True}]])
    fig_trends.add_trace(
        go.Bar(
            x=weekly["year_week"], y=weekly["count"],
            name="Hold Volume",
            marker=dict(color=NVIDIA_GREEN, opacity=0.7),
            hovertemplate="<b>%{x}</b><br>Volume: %{y}<extra></extra>",
        ),
        secondary_y=False,
    )
    fig_trends.add_trace(
        go.Scatter(
            x=weekly["year_week"], y=weekly["avg_duration"],
            name="Avg Duration",
            mode="lines+markers",
            line=dict(color=WARNING, width=2.5),
            marker=dict(size=6, color=WARNING),
            hovertemplate="<b>%{x}</b><br>Avg: %{y:.1f}h<extra></extra>",
        ),
        secondary_y=True,
    )

    # Forecast
    if len(trends["forecast"]) > 0:
        forecast = trends["forecast"]
        last_week_label = weekly["year_week"].iloc[-1]
        forecast_labels = [f"Forecast +{w}w" for w in forecast["week_ahead"]]
        fig_trends.add_trace(
            go.Bar(
                x=forecast_labels, y=forecast["projected_count"],
                name="Projected Volume",
                marker=dict(color=NVIDIA_GREEN, opacity=0.3, line=dict(width=1, color=NVIDIA_GREEN)),
                hovertemplate="<b>%{x}</b><br>Projected: %{y}<extra></extra>",
            ),
            secondary_y=False,
        )
        fig_trends.add_trace(
            go.Scatter(
                x=forecast_labels, y=forecast["projected_avg_duration"],
                name="Projected Duration",
                mode="lines+markers",
                line=dict(color=WARNING, width=2, dash="dash"),
                marker=dict(size=5, color=WARNING, symbol="diamond"),
                hovertemplate="<b>%{x}</b><br>Projected: %{y:.1f}h<extra></extra>",
            ),
            secondary_y=True,
        )

    layout = get_plotly_layout("Weekly Hold Volume & Duration Trend", height=420)
    fig_trends.update_layout(**layout)
    fig_trends.update_layout(
        yaxis=dict(title="Hold Volume", gridcolor=NVIDIA_GRAY_800, tickfont=dict(color=TEXT_SECONDARY)),
        yaxis2=dict(title="Avg Duration (h)", gridcolor="rgba(0,0,0,0)", tickfont=dict(color=TEXT_SECONDARY)),
        legend=dict(orientation="h", y=1.12, font=dict(color=TEXT_SECONDARY)),
        xaxis=dict(tickangle=-45, tickfont=dict(size=10, color=TEXT_SECONDARY)),
    )
    st.plotly_chart(fig_trends, use_container_width=True)

    # Trend indicators
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        direction = trends["count_trend_direction"]
        icon = "downward" if direction == "decreasing" else "upward"
        color = SUCCESS if direction == "decreasing" else ERROR
        st.markdown(f"""
        <div style="background:{CARD_BG}; border:1px solid {CARD_BORDER}; border-radius:8px; padding:20px;">
            <p style="color:{TEXT_SECONDARY}; font-size:12px; text-transform:uppercase; letter-spacing:0.8px; margin-bottom:6px;">Hold Volume Trend</p>
            <p style="color:{color}; font-size:20px; font-weight:700;">Trending {direction.title()}</p>
            <p style="color:{TEXT_MUTED}; font-size:13px;">Based on weekly moving average over {len(weekly)} weeks</p>
        </div>
        """, unsafe_allow_html=True)
    with col_t2:
        direction = trends["duration_trend_direction"]
        color = SUCCESS if direction == "decreasing" else ERROR
        st.markdown(f"""
        <div style="background:{CARD_BG}; border:1px solid {CARD_BORDER}; border-radius:8px; padding:20px;">
            <p style="color:{TEXT_SECONDARY}; font-size:12px; text-transform:uppercase; letter-spacing:0.8px; margin-bottom:6px;">Duration Trend</p>
            <p style="color:{color}; font-size:20px; font-weight:700;">Trending {direction.title()}</p>
            <p style="color:{TEXT_MUTED}; font-size:13px;">Average hold resolution time is {"improving" if direction == "decreasing" else "worsening"}</p>
        </div>
        """, unsafe_allow_html=True)

    # Week-over-week table
    st.markdown(f'<div class="section-header">Week-over-Week Changes</div>', unsafe_allow_html=True)
    wow_table = weekly[["year_week", "count", "avg_duration", "wow_count_change", "wow_duration_change"]].copy()
    wow_table.columns = ["Week", "Hold Volume", "Avg Duration (h)", "Volume WoW %", "Duration WoW %"]
    st.dataframe(wow_table, use_container_width=True, hide_index=True)


# ============================================================
# TAB 6: Recommendations
# ============================================================
with tab6:
    st.markdown(f"""
    <div style="background:{CARD_BG}; border:1px solid {CARD_BORDER}; border-radius:8px; padding:20px; margin-bottom:24px;">
        <p style="color:{NVIDIA_GREEN}; font-size:12px; font-weight:600; text-transform:uppercase; letter-spacing:1px; margin-bottom:4px;">Smart Recommendations Engine</p>
        <p style="color:{TEXT_PRIMARY}; font-size:16px; font-weight:600; margin-bottom:4px;">Data-Driven Action Items</p>
        <p style="color:{TEXT_SECONDARY}; font-size:13px;">Auto-generated from analysis of {len(df)} orders. Each recommendation is backed by specific data patterns, not generic advice.</p>
    </div>
    """, unsafe_allow_html=True)

    recs = generate_recommendations(df)

    for rec in recs:
        priority_lower = rec["priority"].lower()
        priority_color = PRIORITY_COLORS.get(rec["priority"], NVIDIA_GREEN)

        st.markdown(f"""
        <div class="rec-card {priority_lower}">
            <div style="display:flex; align-items:center; gap:12px; margin-bottom:10px;">
                <span class="rec-badge {priority_lower}">{rec["priority"]}</span>
                <span class="rec-category">{rec.get("category", "")}</span>
            </div>
            <div class="rec-finding">{rec["finding"]}</div>
            <div class="rec-impact">{rec["impact"]}</div>
            <div class="rec-action">Recommendation: {rec["recommendation"]}</div>
            <div class="rec-savings">Estimated Impact: {rec.get("estimated_savings", "N/A")}</div>
        </div>
        """, unsafe_allow_html=True)


# ============================================================
# TAB 7: Export
# ============================================================
with tab7:
    st.markdown(f'<div class="section-header">Export Data</div>', unsafe_allow_html=True)

    col_e1, col_e2, col_e3 = st.columns(3)

    with col_e1:
        # Full dataset
        csv_full = df.to_csv(index=False)
        st.download_button(
            "Download Full Dataset (CSV)",
            csv_full,
            "pricing_hold_data.csv",
            "text/csv",
            use_container_width=True,
        )

    with col_e2:
        # Executive summary
        summary_data = pd.DataFrame([summary])
        csv_summary = summary_data.to_csv(index=False)
        st.download_button(
            "Download Executive Summary",
            csv_summary,
            "executive_summary.csv",
            "text/csv",
            use_container_width=True,
        )

    with col_e3:
        # Recommendations
        recs_df = pd.DataFrame(recs)
        csv_recs = recs_df.to_csv(index=False)
        st.download_button(
            "Download Recommendations",
            csv_recs,
            "recommendations.csv",
            "text/csv",
            use_container_width=True,
        )

    # Analysis tables
    st.markdown(f'<div class="section-header">Analysis Reports</div>', unsafe_allow_html=True)

    col_e4, col_e5 = st.columns(2)
    with col_e4:
        reason_csv = hold_reason_breakdown(df).to_csv(index=False)
        st.download_button("Hold Reason Analysis", reason_csv, "hold_reason_analysis.csv", "text/csv", use_container_width=True)
    with col_e5:
        rc_csv = root_cause_analysis(df)["pareto"].to_csv(index=False)
        st.download_button("Root Cause Analysis", rc_csv, "root_cause_analysis.csv", "text/csv", use_container_width=True)


# --- Footer ---
st.markdown(f"""
<div class="nvidia-footer">
    Built by <strong>Arnaud Chacon</strong> as a demonstration project for NVIDIA's WWFO Pricing team.<br>
    Data is synthetically generated for illustration purposes.
</div>
""", unsafe_allow_html=True)
