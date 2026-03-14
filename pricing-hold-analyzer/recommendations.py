"""
Smart Recommendations Engine for PriceOps Analyzer.
Generates specific, actionable, data-driven recommendations based on actual patterns.
"""

import pandas as pd
import numpy as np

SLA_HOURS = 24

# Maps hold reasons to specific, domain-aware recommendations
RECOMMENDATION_TEMPLATES = {
    "Missing Price List": {
        "recommendation": "Implement automated price list sync from BU systems with validation checks. Set up alerts for price list expiry 7 days before expiration to prevent gaps.",
        "savings_per_hold_hours": 6,
    },
    "Discount Approval Pending": {
        "recommendation": "Delegate tiered approval authority to regional pricing leads for discounts under 15%. Implement auto-escalation after 12 hours to prevent approver bottlenecks.",
        "savings_per_hold_hours": 10,
    },
    "Customer Master Data Incomplete": {
        "recommendation": "Implement mandatory data completeness checks at order entry stage. Create automated SAP customer setup workflow triggered by CRM opportunity close.",
        "savings_per_hold_hours": 4,
    },
    "Currency/FX Mismatch": {
        "recommendation": "Configure automated daily FX rate refresh from treasury systems. Add multi-currency validation at order entry to catch mismatches before hold creation.",
        "savings_per_hold_hours": 2,
    },
    "Regional Price Override Required": {
        "recommendation": "Pre-configure country-specific pricing matrices for top 10 markets. Create fast-track approval for competitive bids under $500K with regional manager pre-authorization.",
        "savings_per_hold_hours": 12,
    },
    "Expired Quote": {
        "recommendation": "Implement automated quote expiry alerts at 14, 7, and 3 days before expiration. Auto-extend quotes for strategic accounts with price-hold clauses.",
        "savings_per_hold_hours": 8,
    },
    "System Error": {
        "recommendation": "Implement automated SAP pricing condition validation on order entry. Add duplicate detection logic and interface sync health monitoring with auto-retry.",
        "savings_per_hold_hours": 3,
    },
}

REGION_RECOMMENDATIONS = {
    "APAC": "Establish APAC pricing operations hub in Hong Kong with delegated authority for regional price overrides and FX management. This eliminates timezone delays waiting for US HQ approvals.",
    "EMEA": "Create EMEA pricing desk with authority over EUR/GBP/CHF orders. Pre-configure country-specific pricing for top 5 EMEA markets to reduce Regional Price Override holds.",
    "Americas": "Implement tiered discount auto-approval for Americas: <10% auto-approve, 10-20% regional manager, >20% VP approval. Current flat approval chain creates unnecessary delays on routine discounts.",
}


def generate_recommendations(df):
    """Generate prioritized, data-driven recommendations from the dataset."""
    recommendations = []

    # --- Rule 1: Top hold reason by volume ---
    reason_counts = df["hold_reason"].value_counts()
    top_reason = reason_counts.idxmax()
    top_count = reason_counts.max()
    top_pct = round(top_count / len(df) * 100, 1)
    top_avg_hours = round(df[df["hold_reason"] == top_reason]["hold_duration_hours"].mean(), 1)
    top_total_hours = round(df[df["hold_reason"] == top_reason]["hold_duration_hours"].sum(), 0)
    template = RECOMMENDATION_TEMPLATES.get(top_reason, {})
    est_savings = round(top_count * template.get("savings_per_hold_hours", 4))

    recommendations.append({
        "priority": "HIGH",
        "category": "Hold Volume",
        "finding": f'"{top_reason}" accounts for {top_pct}% of all holds ({top_count} orders), consuming {top_total_hours:,.0f} total hold hours.',
        "impact": f"Average resolution: {top_avg_hours}h. Total business impact: {top_total_hours:,.0f} hours of delayed revenue recognition.",
        "recommendation": template.get("recommendation", "Investigate root causes and implement targeted process improvements."),
        "estimated_savings": f"~{est_savings:,} hours/quarter if resolution time reduced by {template.get('savings_per_hold_hours', 4)}h per hold",
    })

    # --- Rule 2: Region with highest hold rate ---
    region_stats = df.groupby("region").agg(
        count=("order_id", "count"),
        avg_duration=("hold_duration_hours", "mean"),
    ).reset_index()
    overall_avg = df["hold_duration_hours"].mean()
    worst_region = region_stats.loc[region_stats["avg_duration"].idxmax()]
    best_region = region_stats.loc[region_stats["avg_duration"].idxmin()]
    ratio = round(worst_region["avg_duration"] / max(best_region["avg_duration"], 0.1), 2)

    if ratio > 1.15:
        # Find top hold reason for worst region
        worst_df = df[df["region"] == worst_region["region"]]
        worst_top_reason = worst_df["hold_reason"].value_counts().idxmax()

        recommendations.append({
            "priority": "HIGH",
            "category": "Regional Disparity",
            "finding": f'{worst_region["region"]} averages {worst_region["avg_duration"]:.1f}h per hold — {ratio}x higher than {best_region["region"]} ({best_region["avg_duration"]:.1f}h).',
            "impact": f'Top hold reason in {worst_region["region"]}: "{worst_top_reason}". {int(worst_region["count"])} orders affected this period.',
            "recommendation": REGION_RECOMMENDATIONS.get(
                worst_region["region"],
                f"Investigate region-specific bottlenecks in {worst_region['region']} and establish local pricing authority."
            ),
            "estimated_savings": f"Normalizing to company average would save ~{round((worst_region['avg_duration'] - overall_avg) * worst_region['count']):,.0f} hold hours/quarter",
        })

    # --- Rule 3: SLA breach trend ---
    resolved = df[df["hold_status"] == "Resolved"].copy()
    if len(resolved) > 0:
        resolved["month"] = resolved["hold_start"].dt.to_period("M")
        months = sorted(resolved["month"].unique())
        if len(months) >= 2:
            last_breach = resolved[resolved["month"] == months[-1]]
            prev_breach = resolved[resolved["month"] == months[-2]]
            last_rate = (last_breach["hold_duration_hours"] > SLA_HOURS).mean() * 100
            prev_rate = (prev_breach["hold_duration_hours"] > SLA_HOURS).mean() * 100
            rate_change = last_rate - prev_rate
            overall_breach = (resolved["hold_duration_hours"] > SLA_HOURS).mean() * 100

            if rate_change > 5:
                recommendations.append({
                    "priority": "CRITICAL",
                    "category": "SLA Compliance",
                    "finding": f"SLA breach rate increased from {prev_rate:.1f}% to {last_rate:.1f}% month-over-month (+{rate_change:.1f}pp).",
                    "impact": f"Overall SLA breach rate: {overall_breach:.1f}%. {(resolved['hold_duration_hours'] > SLA_HOURS).sum()} orders exceeded the {SLA_HOURS}h target.",
                    "recommendation": "Implement real-time SLA monitoring with automated escalation at 18h mark. Assign dedicated resolver for holds approaching SLA threshold.",
                    "estimated_savings": "Reducing breach rate by 10pp would bring ~15-20 additional orders within SLA monthly",
                })
            elif overall_breach > 20:
                recommendations.append({
                    "priority": "HIGH",
                    "category": "SLA Compliance",
                    "finding": f"SLA breach rate is {overall_breach:.1f}% — over 1 in 5 resolved holds exceed the {SLA_HOURS}h target.",
                    "impact": f"{(resolved['hold_duration_hours'] > SLA_HOURS).sum()} orders breached SLA this period.",
                    "recommendation": "Implement tiered escalation: auto-notify at 12h, escalate to team lead at 18h, VP alert at 24h. Focus on top breach categories first.",
                    "estimated_savings": f"Targeting top breach category could reduce overall breach rate by ~{min(10, overall_breach * 0.3):.0f}pp",
                })

    # --- Rule 4: Approval bottleneck detection ---
    approval_holds = df[df["hold_reason"] == "Discount Approval Pending"]
    if len(approval_holds) > 10:
        avg_approval_time = approval_holds["hold_duration_hours"].mean()
        ooo_count = len(approval_holds[approval_holds["root_cause"] == "Approver out of office"])
        ooo_pct = round(ooo_count / len(approval_holds) * 100, 1)

        if avg_approval_time > 18 or ooo_pct > 20:
            recommendations.append({
                "priority": "MEDIUM",
                "category": "Approval Process",
                "finding": f"Discount approvals average {avg_approval_time:.1f}h. {ooo_pct}% of delays caused by approver unavailability.",
                "impact": f"{len(approval_holds)} orders waiting for discount approval this period. Total hold time: {approval_holds['hold_duration_hours'].sum():,.0f}h.",
                "recommendation": "Implement backup approver chain with automatic delegation when primary approver is OOO. Set up auto-approval for standard discounts under 10% for existing customers.",
                "estimated_savings": f"Auto-approving standard discounts could eliminate ~{round(len(approval_holds) * 0.3)} holds/quarter",
            })

    # --- Rule 5: Pareto — 20% of root causes driving 80% of hold hours ---
    rc_hours = df.groupby("root_cause")["hold_duration_hours"].sum().sort_values(ascending=False)
    cumulative = rc_hours.cumsum() / rc_hours.sum()
    pareto_causes = cumulative[cumulative <= 0.80].index.tolist()
    if len(pareto_causes) > 0:
        total_rc = df["root_cause"].nunique()
        pareto_pct = round(len(pareto_causes) / total_rc * 100, 0)
        top_3 = rc_hours.head(3)

        recommendations.append({
            "priority": "HIGH",
            "category": "Pareto Analysis",
            "finding": f"{len(pareto_causes)} of {total_rc} root causes ({pareto_pct:.0f}%) drive 80% of total hold hours.",
            "impact": f'Top 3: "{top_3.index[0]}" ({top_3.iloc[0]:,.0f}h), "{top_3.index[1]}" ({top_3.iloc[1]:,.0f}h), "{top_3.index[2]}" ({top_3.iloc[2]:,.0f}h).' if len(top_3) >= 3 else "",
            "recommendation": f'Focus improvement efforts on these {len(pareto_causes)} root causes. Start with "{rc_hours.index[0]}" which alone accounts for {rc_hours.iloc[0] / rc_hours.sum() * 100:.1f}% of all hold hours.',
            "estimated_savings": f"Addressing top 3 root causes could reduce total hold hours by ~{round(top_3.sum() / rc_hours.sum() * 100)}%",
        })

    # --- Rule 6: New product launch impact (November spike) ---
    df_copy = df.copy()
    df_copy["month"] = df_copy["hold_start"].dt.month
    nov_missing = df_copy[(df_copy["month"] == 11) & (df_copy["hold_reason"] == "Missing Price List")]
    oct_missing = df_copy[(df_copy["month"] == 10) & (df_copy["hold_reason"] == "Missing Price List")]

    if len(oct_missing) > 0 and len(nov_missing) > len(oct_missing) * 1.2:
        spike_pct = round((len(nov_missing) - len(oct_missing)) / len(oct_missing) * 100, 0)
        recommendations.append({
            "priority": "MEDIUM",
            "category": "Product Launch Process",
            "finding": f'"Missing Price List" holds spiked {spike_pct:.0f}% in November vs October ({len(nov_missing)} vs {len(oct_missing)}), coinciding with new product launches.',
            "impact": f"New products without configured pricing create downstream order holds averaging {nov_missing['hold_duration_hours'].mean():.1f}h each.",
            "recommendation": "Integrate price list creation into product launch checklist. Require pricing configuration sign-off before product goes live in order system. Create T-14 day launch pricing readiness check.",
            "estimated_savings": f"Preventing launch-related holds could save ~{round(nov_missing['hold_duration_hours'].sum()):,.0f} hold hours during launch months",
        })

    # --- Rule 7: Repeat offender customers ---
    customer_holds = df["customer_name"].value_counts()
    repeat_threshold = customer_holds.quantile(0.90)
    repeat_customers = customer_holds[customer_holds >= max(repeat_threshold, 5)]

    if len(repeat_customers) >= 2:
        top_customer = repeat_customers.index[0]
        top_customer_count = repeat_customers.iloc[0]
        top_customer_reason = df[df["customer_name"] == top_customer]["hold_reason"].value_counts().idxmax()

        recommendations.append({
            "priority": "MEDIUM",
            "category": "Customer Experience",
            "finding": f"{len(repeat_customers)} customers have recurring holds. {top_customer} leads with {top_customer_count} holds, primarily due to \"{top_customer_reason}\".",
            "impact": f"Repeat holds signal systemic issues in customer setup or pricing configuration, and risk damaging key account relationships.",
            "recommendation": f'Conduct root cause review for top repeat-hold customers. For {top_customer}, address "{top_customer_reason}" with a dedicated account pricing profile. Implement customer health scoring to flag accounts approaching hold thresholds.',
            "estimated_savings": f"Reducing repeat-customer holds by 50% could eliminate ~{round(repeat_customers.sum() * 0.5)} holds/quarter",
        })

    # --- Rule 8: Escalation rate analysis ---
    escalated = df[df["hold_status"] == "Escalated"]
    escalation_rate = len(escalated) / max(len(df), 1) * 100
    if escalation_rate > 8:
        esc_top_reason = escalated["hold_reason"].value_counts().idxmax()
        esc_avg_duration = escalated["hold_duration_hours"].mean()
        recommendations.append({
            "priority": "HIGH",
            "category": "Escalation Management",
            "finding": f"Escalation rate is {escalation_rate:.1f}% ({len(escalated)} orders). Top escalation reason: \"{esc_top_reason}\".",
            "impact": f"Escalated holds average {esc_avg_duration:.1f}h — significantly above the {SLA_HOURS}h SLA target.",
            "recommendation": f"Create fast-track resolution path for \"{esc_top_reason}\" escalations. Implement proactive escalation triggers based on hold age and priority rather than waiting for manual escalation.",
            "estimated_savings": f"Reducing escalations by 30% through proactive management could save ~{round(len(escalated) * 0.3 * esc_avg_duration):,.0f} hold hours/quarter",
        })

    # --- Rule 9: Regional Price Override trend (problem area) ---
    rpo = df[df["hold_reason"] == "Regional Price Override Required"].copy()
    if len(rpo) > 5:
        rpo["month"] = rpo["hold_start"].dt.to_period("M")
        monthly_rpo = rpo.groupby("month").size()
        if len(monthly_rpo) >= 3:
            trend = np.polyfit(range(len(monthly_rpo)), monthly_rpo.values, 1)
            if trend[0] > 0.5:  # Increasing trend
                recommendations.append({
                    "priority": "CRITICAL",
                    "category": "Trending Issue",
                    "finding": f'"Regional Price Override Required" is trending upward — growing by ~{trend[0]:.1f} holds/month over the period.',
                    "impact": f"These holds average {rpo['hold_duration_hours'].mean():.1f}h (among the longest). {len(rpo)} total this period.",
                    "recommendation": "This is the fastest-growing hold category. Pre-configure regional pricing matrices for top 15 country/product combinations. Establish regional pricing authority to approve overrides locally without HQ escalation.",
                    "estimated_savings": f"Local approval authority could reduce resolution time from {rpo['hold_duration_hours'].mean():.1f}h to ~8h, saving {round(rpo['hold_duration_hours'].sum() * 0.5):,.0f}h",
                })

    # Sort by priority
    priority_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    recommendations.sort(key=lambda x: priority_order.get(x["priority"], 99))

    return recommendations
