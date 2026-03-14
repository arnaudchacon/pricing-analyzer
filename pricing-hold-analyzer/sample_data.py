"""
Generate realistic sample data for the PriceOps Analyzer.
500 sales orders spanning Oct 2025 - Jan 2026 with realistic NVIDIA pricing hold patterns.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

# --- Constants ---

HOLD_REASONS = {
    "Missing Price List": {
        "weight": 0.25,
        "root_causes": [
            "BU price list not uploaded",
            "New product not in system",
            "Price list version expired",
        ],
        "resolutions": [
            "Price list uploaded by BU team",
            "Manual price entry",
            "Escalated to product management",
        ],
        "duration_range": (8, 16),
        "duration_std": 4,
    },
    "Discount Approval Pending": {
        "weight": 0.20,
        "root_causes": [
            "Discount exceeds threshold",
            "Non-standard deal structure",
            "Approver out of office",
        ],
        "resolutions": [
            "Approved by regional manager",
            "Rejected - repriced",
            "Auto-approved after escalation",
        ],
        "duration_range": (12, 36),
        "duration_std": 8,
    },
    "Customer Master Data Incomplete": {
        "weight": 0.18,
        "root_causes": [
            "Missing billing address",
            "Tax ID not on file",
            "Credit check pending",
            "New customer not set up in SAP",
        ],
        "resolutions": [
            "Customer data updated",
            "Credit approved",
            "Customer contacted for info",
        ],
        "duration_range": (4, 12),
        "duration_std": 3,
    },
    "Currency/FX Mismatch": {
        "weight": 0.12,
        "root_causes": [
            "Order currency differs from price list",
            "FX rate expired",
            "Multi-currency order",
        ],
        "resolutions": [
            "Currency corrected",
            "FX rate updated",
            "Manual override applied",
        ],
        "duration_range": (2, 6),
        "duration_std": 2,
    },
    "Regional Price Override Required": {
        "weight": 0.10,
        "root_causes": [
            "Country-specific pricing not configured",
            "Competitive bid requires special pricing",
            "Government/education discount",
        ],
        "resolutions": [
            "Regional price approved",
            "Standard pricing applied",
            "Escalated to HQ",
        ],
        "duration_range": (16, 48),
        "duration_std": 10,
    },
    "Expired Quote": {
        "weight": 0.08,
        "root_causes": [
            "Quote validity exceeded",
            "Customer delayed PO",
            "Price increase since quote",
        ],
        "resolutions": [
            "Quote reissued",
            "Original price honored",
            "New quote with updated pricing",
        ],
        "duration_range": (8, 24),
        "duration_std": 6,
    },
    "System Error": {
        "weight": 0.07,
        "root_causes": [
            "SAP pricing condition error",
            "Duplicate order entry",
            "Interface sync failure",
        ],
        "resolutions": [
            "SAP config corrected",
            "Duplicate removed",
            "Manual reprocessing",
        ],
        "duration_range": (2, 8),
        "duration_std": 2,
    },
}

REGIONS = {
    "APAC": {
        "weight": 0.40,
        "sub_regions": {
            "Hong Kong": 0.20,
            "Japan": 0.18,
            "Korea": 0.15,
            "Singapore": 0.15,
            "India": 0.15,
            "Australia": 0.10,
            "Taiwan": 0.07,
        },
        "customers": {
            "Hong Kong": ["Lenovo Hong Kong Ltd", "ASUS Computer HK", "MSI Computer Hong Kong"],
            "Japan": ["Dell Technologies Japan", "NEC Corporation Japan", "Fujitsu Japan"],
            "Korea": ["Samsung Electronics Korea", "LG Electronics Korea"],
            "Singapore": ["Supermicro Singapore", "Razer Singapore"],
            "India": ["Tata Consultancy Services India", "Infosys Technologies"],
            "Australia": ["Fujitsu Australia", "Data#3 Australia"],
            "Taiwan": ["Gigabyte Technology Taiwan", "ASUS Taiwan HQ"],
        },
        "currencies": {
            "Hong Kong": "HKD",
            "Japan": "JPY",
            "Korea": "KRW",
            "Singapore": "SGD",
            "India": "INR",
            "Australia": "AUD",
            "Taiwan": "TWD",
        },
    },
    "EMEA": {
        "weight": 0.30,
        "sub_regions": {
            "Germany": 0.25,
            "UK": 0.20,
            "France": 0.20,
            "Switzerland": 0.15,
            "Netherlands": 0.10,
            "Sweden": 0.10,
        },
        "customers": {
            "Germany": ["BMW Group Germany", "Siemens Digital Industries", "Volkswagen Group", "Mercedes-Benz AG"],
            "UK": ["BAE Systems UK", "ARM Holdings UK"],
            "France": ["Dassault Systemes France", "Renault Group"],
            "Switzerland": ["CERN Switzerland", "ABB Switzerland"],
            "Netherlands": ["ASML Netherlands", "Philips Healthcare"],
            "Sweden": ["Ericsson Sweden", "Volvo Group"],
        },
        "currencies": {
            "Germany": "EUR",
            "UK": "GBP",
            "France": "EUR",
            "Switzerland": "CHF",
            "Netherlands": "EUR",
            "Sweden": "SEK",
        },
    },
    "Americas": {
        "weight": 0.30,
        "sub_regions": {
            "US West": 0.30,
            "US East": 0.30,
            "Canada": 0.20,
            "Brazil": 0.20,
        },
        "customers": {
            "US West": ["Amazon Web Services", "Meta Platforms Inc", "Tesla Inc", "Stanford University"],
            "US East": ["Microsoft Azure", "Lockheed Martin", "Johns Hopkins University"],
            "Canada": ["Shopify Canada", "BlackBerry QNX"],
            "Brazil": ["Petrobras Brazil", "Embraer SA"],
        },
        "currencies": {
            "US West": "USD",
            "US East": "USD",
            "Canada": "CAD",
            "Brazil": "BRL",
        },
    },
}

BUSINESS_UNITS = {
    "Data Center": {"weight": 0.30, "products": ["DGX", "HGX", "Tesla/A100"], "value_range": (50000, 2000000)},
    "Gaming": {"weight": 0.25, "products": ["GeForce RTX"], "value_range": (5000, 200000)},
    "Professional Visualization": {"weight": 0.15, "products": ["Quadro"], "value_range": (10000, 500000)},
    "Automotive": {"weight": 0.15, "products": ["DRIVE"], "value_range": (100000, 5000000)},
    "OEM": {"weight": 0.10, "products": ["GeForce RTX", "Quadro"], "value_range": (20000, 800000)},
    "Edge AI": {"weight": 0.05, "products": ["Jetson"], "value_range": (5000, 150000)},
}

SALES_REPS = [
    "James Chen", "Sarah Kim", "Michael Wong", "Emily Zhang", "David Liu",
    "Anna Mueller", "Pierre Durand", "Thomas Fischer", "Sophie Martin",
    "John Smith", "Maria Garcia", "Robert Johnson", "Lisa Anderson",
    "Kevin Park", "Yuki Tanaka", "Raj Patel", "Priya Sharma",
]

PRIORITIES = {"Standard": 0.60, "Urgent": 0.30, "Critical": 0.10}


def generate_sample_data(n_orders=500, seed=42):
    """Generate n_orders of realistic pricing hold data."""
    np.random.seed(seed)

    # Date range: Oct 1 2025 - Jan 31 2026
    start_date = datetime(2025, 10, 1)
    end_date = datetime(2026, 1, 31)
    date_range_days = (end_date - start_date).days

    records = []

    # Pre-compute weights
    reason_names = list(HOLD_REASONS.keys())
    reason_weights = np.array([HOLD_REASONS[r]["weight"] for r in reason_names])

    region_names = list(REGIONS.keys())
    region_weights = np.array([REGIONS[r]["weight"] for r in region_names])

    bu_names = list(BUSINESS_UNITS.keys())
    bu_weights = np.array([BUSINESS_UNITS[b]["weight"] for b in bu_names])

    priority_names = list(PRIORITIES.keys())
    priority_weights = np.array(list(PRIORITIES.values()))

    for i in range(n_orders):
        # --- Region & sub-region ---
        region = np.random.choice(region_names, p=region_weights)
        region_data = REGIONS[region]
        sub_region_names = list(region_data["sub_regions"].keys())
        sub_region_weights = np.array(list(region_data["sub_regions"].values()))
        sub_region_weights /= sub_region_weights.sum()
        sub_region = np.random.choice(sub_region_names, p=sub_region_weights)

        # Customer
        customer = np.random.choice(region_data["customers"][sub_region])
        currency = region_data["currencies"][sub_region]

        # --- Business Unit ---
        bu = np.random.choice(bu_names, p=bu_weights)
        bu_data = BUSINESS_UNITS[bu]
        product_line = np.random.choice(bu_data["products"])

        # --- Hold Reason with regional bias ---
        adjusted_weights = reason_weights.copy()
        if region == "APAC":
            # Higher Currency/FX and Regional Price Override in APAC
            idx_fx = reason_names.index("Currency/FX Mismatch")
            idx_rpo = reason_names.index("Regional Price Override Required")
            adjusted_weights[idx_fx] *= 1.5
            adjusted_weights[idx_rpo] *= 1.4
        elif region == "Americas":
            # More Discount Approval in Americas (bigger deals)
            idx_disc = reason_names.index("Discount Approval Pending")
            adjusted_weights[idx_disc] *= 1.4

        # November spike for Missing Price List (new product launches)
        order_day_offset = np.random.randint(0, date_range_days)
        order_date = start_date + timedelta(days=order_day_offset)

        if order_date.month == 11:
            idx_mpl = reason_names.index("Missing Price List")
            adjusted_weights[idx_mpl] *= 1.6

        # Regional Price Override trending UP over time (problem area)
        month_idx = (order_date.year - 2025) * 12 + order_date.month - 10  # 0-3
        idx_rpo = reason_names.index("Regional Price Override Required")
        adjusted_weights[idx_rpo] *= (1 + 0.35 * month_idx)

        adjusted_weights /= adjusted_weights.sum()
        hold_reason = np.random.choice(reason_names, p=adjusted_weights)
        reason_data = HOLD_REASONS[hold_reason]

        # Root cause and resolution
        root_cause = np.random.choice(reason_data["root_causes"])
        resolution_action = np.random.choice(reason_data["resolutions"])

        # --- Dates ---
        hold_start = order_date + timedelta(hours=np.random.uniform(0.5, 8))

        # Duration with slight downward trend over time (improvement story)
        base_duration = np.random.uniform(*reason_data["duration_range"])
        duration_noise = np.random.normal(0, reason_data["duration_std"])
        trend_factor = 1 - (month_idx * 0.05)  # 5% improvement per month
        hold_duration = max(0.5, (base_duration + duration_noise) * trend_factor)

        # Add some outliers (72+ hours)
        if np.random.random() < 0.03:
            hold_duration = np.random.uniform(72, 120)

        # --- Status ---
        status_roll = np.random.random()
        if status_roll < 0.70:
            hold_status = "Resolved"
            hold_end = hold_start + timedelta(hours=hold_duration)
        elif status_roll < 0.90:
            hold_status = "Open"
            hold_end = None
            hold_duration = (datetime(2026, 1, 31) - hold_start).total_seconds() / 3600
            # Cap open holds to reasonable values
            hold_duration = min(hold_duration, np.random.uniform(4, 72))
        else:
            hold_status = "Escalated"
            hold_end = None
            hold_duration = np.random.uniform(24, 96)

        hold_duration = round(hold_duration, 1)

        # --- Order Value ---
        value_min, value_max = bu_data["value_range"]
        order_value = round(np.random.lognormal(
            mean=np.log((value_min + value_max) / 3),
            sigma=0.6
        ))
        order_value = max(value_min, min(value_max * 2, order_value))

        # --- Priority ---
        priority = np.random.choice(priority_names, p=priority_weights)
        if hold_duration > 48:
            priority = np.random.choice(["Urgent", "Critical"], p=[0.4, 0.6])

        # --- Order ID ---
        region_code = {"APAC": "HK", "EMEA": "EU", "Americas": "US"}[region]
        order_id = f"SO-{order_date.year}-{region_code}-{i+1:05d}"

        # --- Sales Rep ---
        sales_rep = np.random.choice(SALES_REPS)

        records.append({
            "order_id": order_id,
            "order_date": order_date.strftime("%Y-%m-%d"),
            "hold_start": hold_start.strftime("%Y-%m-%d %H:%M"),
            "hold_end": hold_end.strftime("%Y-%m-%d %H:%M") if hold_end else "",
            "hold_duration_hours": hold_duration,
            "hold_status": hold_status,
            "hold_reason": hold_reason,
            "root_cause": root_cause,
            "resolution_action": resolution_action if hold_status == "Resolved" else "",
            "business_unit": bu,
            "region": region,
            "sub_region": sub_region,
            "customer_name": customer,
            "product_line": product_line,
            "currency": currency,
            "order_value": order_value,
            "sales_rep": sales_rep,
            "priority": priority,
        })

    df = pd.DataFrame(records)
    df["order_date"] = pd.to_datetime(df["order_date"])
    df["hold_start"] = pd.to_datetime(df["hold_start"])
    df["hold_end"] = pd.to_datetime(df["hold_end"], errors="coerce")

    return df


def save_sample_csv(df=None, path=None):
    """Save sample data to CSV."""
    if df is None:
        df = generate_sample_data()
    if path is None:
        path = os.path.join(os.path.dirname(__file__), "data", "sample_orders.csv")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False)
    return path


if __name__ == "__main__":
    df = generate_sample_data()
    path = save_sample_csv(df)
    print(f"Generated {len(df)} orders -> {path}")
    print(f"\nHold reason distribution:")
    print(df["hold_reason"].value_counts())
    print(f"\nRegion distribution:")
    print(df["region"].value_counts())
    print(f"\nStatus distribution:")
    print(df["hold_status"].value_counts())
