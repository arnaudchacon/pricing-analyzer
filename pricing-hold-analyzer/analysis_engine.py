"""
Core analysis engine for the PriceOps Analyzer.
Computes hold reason breakdowns, duration analysis, root cause Pareto,
region/BU heatmaps, trends, and forecasting.
"""

import pandas as pd
import numpy as np


SLA_HOURS = 24  # Default SLA target


def compute_executive_summary(df, sla_hours=SLA_HOURS):
    """Compute top-level KPI metrics with trend deltas."""
    now = df["hold_start"].max()
    mid = now - pd.Timedelta(days=45)

    current = df[df["hold_start"] >= mid]
    previous = df[df["hold_start"] < mid]

    total_on_hold = len(df[df["hold_status"].isin(["Open", "Escalated"])])
    avg_duration = df["hold_duration_hours"].mean()
    resolved = df[df["hold_status"] == "Resolved"]
    resolution_rate = (
        (resolved["hold_duration_hours"] <= sla_hours).sum() / max(len(resolved), 1) * 100
    )

    # Deltas
    prev_avg = previous["hold_duration_hours"].mean() if len(previous) > 0 else avg_duration
    curr_avg = current["hold_duration_hours"].mean() if len(current) > 0 else avg_duration
    duration_delta = round(curr_avg - prev_avg, 1)

    prev_resolved = previous[previous["hold_status"] == "Resolved"]
    prev_rate = (
        (prev_resolved["hold_duration_hours"] <= sla_hours).sum()
        / max(len(prev_resolved), 1)
        * 100
    ) if len(prev_resolved) > 0 else resolution_rate
    curr_resolved = current[current["hold_status"] == "Resolved"]
    curr_rate = (
        (curr_resolved["hold_duration_hours"] <= sla_hours).sum()
        / max(len(curr_resolved), 1)
        * 100
    ) if len(curr_resolved) > 0 else resolution_rate
    rate_delta = round(curr_rate - prev_rate, 1)

    top_reason = df["hold_reason"].value_counts().idxmax()
    top_reason_count = df["hold_reason"].value_counts().max()

    return {
        "total_on_hold": total_on_hold,
        "avg_duration": round(avg_duration, 1),
        "duration_delta": duration_delta,
        "resolution_rate": round(resolution_rate, 1),
        "rate_delta": rate_delta,
        "top_reason": top_reason,
        "top_reason_count": top_reason_count,
        "total_orders": len(df),
    }


def hold_reason_breakdown(df):
    """Distribution of hold reasons with stats."""
    grouped = df.groupby("hold_reason").agg(
        count=("order_id", "count"),
        avg_duration=("hold_duration_hours", "mean"),
        total_hours=("hold_duration_hours", "sum"),
        median_duration=("hold_duration_hours", "median"),
    ).reset_index()

    grouped["pct_of_total"] = (grouped["count"] / grouped["count"].sum() * 100).round(1)
    grouped["avg_duration"] = grouped["avg_duration"].round(1)
    grouped["total_hours"] = grouped["total_hours"].round(0)
    grouped["median_duration"] = grouped["median_duration"].round(1)

    # Month-over-month trend
    df_copy = df.copy()
    df_copy["month"] = df_copy["hold_start"].dt.to_period("M")
    months = sorted(df_copy["month"].unique())
    if len(months) >= 2:
        last_month = df_copy[df_copy["month"] == months[-1]]
        prev_month = df_copy[df_copy["month"] == months[-2]]
        last_counts = last_month["hold_reason"].value_counts()
        prev_counts = prev_month["hold_reason"].value_counts()
        trend = {}
        for reason in grouped["hold_reason"]:
            lc = last_counts.get(reason, 0)
            pc = prev_counts.get(reason, 0)
            if pc > 0:
                trend[reason] = round((lc - pc) / pc * 100, 1)
            else:
                trend[reason] = 0.0
        grouped["mom_trend_pct"] = grouped["hold_reason"].map(trend)
    else:
        grouped["mom_trend_pct"] = 0.0

    return grouped.sort_values("count", ascending=False)


def duration_analysis(df, sla_hours=SLA_HOURS):
    """Duration distribution, box plot data, and SLA breach rates."""
    bins = [0, 4, 8, 24, 48, float("inf")]
    labels = ["0-4h", "4-8h", "8-24h", "24-48h", "48h+"]
    df_copy = df.copy()
    df_copy["duration_bucket"] = pd.cut(
        df_copy["hold_duration_hours"], bins=bins, labels=labels, right=True
    )
    histogram_data = df_copy["duration_bucket"].value_counts().reindex(labels).fillna(0)

    # SLA breach by reason
    resolved = df[df["hold_status"] == "Resolved"].copy()
    breach_by_reason = resolved.groupby("hold_reason").apply(
        lambda x: (x["hold_duration_hours"] > sla_hours).sum() / max(len(x), 1) * 100
    ).round(1).reset_index()
    breach_by_reason.columns = ["hold_reason", "sla_breach_pct"]

    # Daily trend
    daily = df.copy()
    daily["date"] = daily["hold_start"].dt.date
    daily_trend = daily.groupby("date")["hold_duration_hours"].mean().reset_index()
    daily_trend.columns = ["date", "avg_duration"]
    daily_trend["date"] = pd.to_datetime(daily_trend["date"])

    return {
        "histogram": histogram_data,
        "duration_buckets": df_copy,
        "breach_by_reason": breach_by_reason.sort_values("sla_breach_pct", ascending=False),
        "daily_trend": daily_trend,
    }


def root_cause_analysis(df):
    """Root cause Pareto and flow data."""
    # Pareto by total hold hours
    rc_stats = df.groupby("root_cause").agg(
        count=("order_id", "count"),
        total_hours=("hold_duration_hours", "sum"),
        avg_duration=("hold_duration_hours", "mean"),
    ).reset_index().sort_values("total_hours", ascending=False)

    rc_stats["cumulative_hours"] = rc_stats["total_hours"].cumsum()
    rc_stats["cumulative_pct"] = (
        rc_stats["cumulative_hours"] / rc_stats["total_hours"].sum() * 100
    ).round(1)
    rc_stats["avg_duration"] = rc_stats["avg_duration"].round(1)
    rc_stats["total_hours"] = rc_stats["total_hours"].round(0)

    # Sankey: reason -> root cause -> resolution
    resolved = df[df["hold_status"] == "Resolved"]
    flow = resolved.groupby(
        ["hold_reason", "root_cause", "resolution_action"]
    ).size().reset_index(name="count")

    return {
        "pareto": rc_stats,
        "flow": flow,
    }


def region_bu_analysis(df, sla_hours=SLA_HOURS):
    """Heatmaps and comparisons by region and business unit."""
    # Heatmap: BU x Region hold count
    heatmap_count = pd.pivot_table(
        df, values="order_id", index="business_unit",
        columns="region", aggfunc="count", fill_value=0,
    )

    # Heatmap: BU x Region avg duration
    heatmap_duration = pd.pivot_table(
        df, values="hold_duration_hours", index="business_unit",
        columns="region", aggfunc="mean", fill_value=0,
    ).round(1)

    # Region stats
    region_stats = df.groupby("region").agg(
        count=("order_id", "count"),
        avg_duration=("hold_duration_hours", "mean"),
        total_hours=("hold_duration_hours", "sum"),
    ).reset_index()
    region_stats["avg_duration"] = region_stats["avg_duration"].round(1)

    # BU breakdown with SLA
    bu_stats = df.groupby("business_unit").agg(
        count=("order_id", "count"),
        avg_duration=("hold_duration_hours", "mean"),
        total_hours=("hold_duration_hours", "sum"),
    ).reset_index()

    resolved = df[df["hold_status"] == "Resolved"]
    bu_breach = resolved.groupby("business_unit").apply(
        lambda x: round((x["hold_duration_hours"] > sla_hours).sum() / max(len(x), 1) * 100, 1)
    ).reset_index()
    bu_breach.columns = ["business_unit", "sla_breach_pct"]
    bu_stats = bu_stats.merge(bu_breach, on="business_unit", how="left")
    bu_stats["avg_duration"] = bu_stats["avg_duration"].round(1)

    return {
        "heatmap_count": heatmap_count,
        "heatmap_duration": heatmap_duration,
        "region_stats": region_stats,
        "bu_stats": bu_stats.sort_values("count", ascending=False),
    }


def trend_analysis(df):
    """Weekly trends and simple forecast."""
    df_copy = df.copy()
    df_copy["week"] = df_copy["hold_start"].dt.isocalendar().week.astype(int)
    df_copy["year_week"] = df_copy["hold_start"].dt.strftime("%Y-W%U")

    weekly = df_copy.groupby("year_week").agg(
        count=("order_id", "count"),
        avg_duration=("hold_duration_hours", "mean"),
        date_min=("hold_start", "min"),
    ).reset_index().sort_values("date_min")

    weekly["avg_duration"] = weekly["avg_duration"].round(1)

    # Week-over-week changes
    weekly["wow_count_change"] = weekly["count"].pct_change().fillna(0).round(3) * 100
    weekly["wow_duration_change"] = weekly["avg_duration"].pct_change().fillna(0).round(3) * 100

    # Simple linear regression forecast
    if len(weekly) >= 4:
        x = np.arange(len(weekly))
        count_slope = np.polyfit(x, weekly["count"].values, 1)[0]
        duration_slope = np.polyfit(x, weekly["avg_duration"].values, 1)[0]

        # Forecast next 4 weeks
        forecast_weeks = 4
        last_count = weekly["count"].iloc[-1]
        last_duration = weekly["avg_duration"].iloc[-1]

        forecast = pd.DataFrame({
            "week_ahead": range(1, forecast_weeks + 1),
            "projected_count": [round(last_count + count_slope * w) for w in range(1, forecast_weeks + 1)],
            "projected_avg_duration": [round(last_duration + duration_slope * w, 1) for w in range(1, forecast_weeks + 1)],
        })
    else:
        forecast = pd.DataFrame()

    return {
        "weekly": weekly,
        "forecast": forecast,
        "count_trend_direction": "decreasing" if len(weekly) >= 4 and np.polyfit(np.arange(len(weekly)), weekly["count"].values, 1)[0] < 0 else "increasing",
        "duration_trend_direction": "decreasing" if len(weekly) >= 4 and np.polyfit(np.arange(len(weekly)), weekly["avg_duration"].values, 1)[0] < 0 else "increasing",
    }
