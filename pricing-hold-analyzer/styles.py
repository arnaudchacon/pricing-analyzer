"""
NVIDIA-inspired styling for the PriceOps Analyzer.
Uses the official NVIDIA design system colors and typography.
"""

# --- Color constants ---
NVIDIA_GREEN = "#76B900"
NVIDIA_GREEN_DARK = "#265600"
NVIDIA_GREEN_LIGHT = "#BFF230"
NVIDIA_BLACK = "#000000"
NVIDIA_GRAY_950 = "#161616"
NVIDIA_GRAY_900 = "#222222"
NVIDIA_GRAY_800 = "#313131"
NVIDIA_GRAY_700 = "#4B4B4B"
NVIDIA_GRAY_600 = "#636363"
NVIDIA_GRAY_500 = "#757575"
NVIDIA_GRAY_400 = "#898989"
NVIDIA_GRAY_300 = "#A7A7A7"
NVIDIA_GRAY_200 = "#CCCCCC"
NVIDIA_GRAY_100 = "#E0E0E0"
NVIDIA_GRAY_050 = "#EEEEEE"
NVIDIA_GRAY_025 = "#F7F7F7"
NVIDIA_WHITE = "#FFFFFF"

BACKGROUND = "#0C0C0C"
CARD_BG = "#161616"
CARD_BORDER = "#313131"
TEXT_PRIMARY = "#FFFFFF"
TEXT_SECONDARY = "#A7A7A7"
TEXT_MUTED = "#757575"

SUCCESS = "#76B900"
WARNING = "#F9C500"
ERROR = "#E52020"
INFO = "#0074DF"

# Chart palette matching NVIDIA's design system
CHART_COLORS = [
    "#76B900",  # NVIDIA green
    "#0074DF",  # blue
    "#F9C500",  # yellow
    "#E52020",  # red
    "#C359EF",  # purple
    "#D2308E",  # fuchsia
    "#1DBBA4",  # teal
    "#FC79CA",  # fuchsia light
]

PRIORITY_COLORS = {
    "CRITICAL": "#E52020",
    "HIGH": "#F9C500",
    "MEDIUM": "#0074DF",
    "LOW": "#76B900",
}

STATUS_COLORS = {
    "Resolved": "#76B900",
    "Open": "#F9C500",
    "Escalated": "#E52020",
}


def get_custom_css():
    """Return custom CSS for the Streamlit app with NVIDIA dark theme."""
    return f"""
    <style>
        /* --- Import NVIDIA-style font --- */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

        /* --- Global dark theme --- */
        .stApp {{
            background-color: {BACKGROUND};
            color: {TEXT_PRIMARY};
            font-family: 'Inter', Arial, Helvetica, sans-serif;
        }}

        /* --- Header --- */
        .nvidia-header {{
            background: linear-gradient(135deg, {NVIDIA_GRAY_950} 0%, {NVIDIA_GRAY_900} 100%);
            border-bottom: 3px solid {NVIDIA_GREEN};
            padding: 28px 32px 20px 32px;
            margin: -1rem -1rem 2rem -1rem;
        }}
        .nvidia-header h1 {{
            color: {NVIDIA_WHITE};
            font-size: 32px;
            font-weight: 700;
            margin: 0 0 2px 0;
            letter-spacing: -0.5px;
        }}
        .nvidia-header h1 span {{
            color: {NVIDIA_GREEN};
        }}
        .nvidia-header p {{
            color: {TEXT_SECONDARY};
            font-size: 14px;
            margin: 0;
            font-weight: 400;
        }}

        /* --- Metric cards --- */
        .metric-card {{
            background: {CARD_BG};
            border: 1px solid {CARD_BORDER};
            border-radius: 8px;
            padding: 20px 24px;
            transition: border-color 200ms ease;
        }}
        .metric-card:hover {{
            border-color: {NVIDIA_GREEN};
        }}
        .metric-card .metric-label {{
            color: {TEXT_SECONDARY};
            font-size: 12px;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.8px;
            margin-bottom: 8px;
        }}
        .metric-card .metric-value {{
            color: {NVIDIA_WHITE};
            font-size: 32px;
            font-weight: 700;
            line-height: 1;
            margin-bottom: 6px;
        }}
        .metric-card .metric-delta {{
            font-size: 13px;
            font-weight: 500;
        }}
        .metric-delta.positive {{ color: {SUCCESS}; }}
        .metric-delta.negative {{ color: {ERROR}; }}

        /* --- Override Streamlit metric styling --- */
        [data-testid="stMetric"] {{
            background: {CARD_BG};
            border: 1px solid {CARD_BORDER};
            border-radius: 8px;
            padding: 16px 20px;
        }}
        [data-testid="stMetricLabel"] {{
            color: {TEXT_SECONDARY} !important;
        }}
        [data-testid="stMetricLabel"] p {{
            color: {TEXT_SECONDARY} !important;
            font-size: 12px !important;
            text-transform: uppercase;
            letter-spacing: 0.8px;
            font-weight: 500;
        }}
        [data-testid="stMetricValue"] {{
            color: {NVIDIA_WHITE} !important;
            font-size: 28px !important;
            font-weight: 700 !important;
        }}
        [data-testid="stMetricDelta"] {{
            font-weight: 500;
        }}

        /* --- Tabs styling --- */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 0px;
            background: {NVIDIA_GRAY_950};
            border-radius: 8px;
            padding: 4px;
            border: 1px solid {CARD_BORDER};
        }}
        .stTabs [data-baseweb="tab"] {{
            color: {TEXT_SECONDARY};
            font-weight: 500;
            font-size: 14px;
            padding: 10px 20px;
            border-radius: 6px;
            background: transparent;
        }}
        .stTabs [aria-selected="true"] {{
            background: {NVIDIA_GREEN} !important;
            color: {NVIDIA_BLACK} !important;
            font-weight: 600;
        }}
        .stTabs [data-baseweb="tab-highlight"] {{
            display: none;
        }}
        .stTabs [data-baseweb="tab-border"] {{
            display: none;
        }}

        /* --- Section headers --- */
        .section-header {{
            color: {NVIDIA_WHITE};
            font-size: 20px;
            font-weight: 600;
            margin: 24px 0 16px 0;
            padding-bottom: 8px;
            border-bottom: 2px solid {NVIDIA_GREEN};
            display: inline-block;
        }}

        /* --- Recommendation cards --- */
        .rec-card {{
            background: {CARD_BG};
            border: 1px solid {CARD_BORDER};
            border-radius: 8px;
            padding: 24px;
            margin-bottom: 16px;
            border-left: 4px solid;
            transition: border-color 200ms ease, transform 200ms ease;
        }}
        .rec-card:hover {{
            transform: translateY(-1px);
        }}
        .rec-card.critical {{ border-left-color: {ERROR}; }}
        .rec-card.high {{ border-left-color: {WARNING}; }}
        .rec-card.medium {{ border-left-color: {INFO}; }}
        .rec-card.low {{ border-left-color: {SUCCESS}; }}

        .rec-badge {{
            display: inline-block;
            padding: 3px 10px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 10px;
        }}
        .rec-badge.critical {{ background: {ERROR}; color: white; }}
        .rec-badge.high {{ background: {WARNING}; color: {NVIDIA_BLACK}; }}
        .rec-badge.medium {{ background: {INFO}; color: white; }}
        .rec-badge.low {{ background: {SUCCESS}; color: {NVIDIA_BLACK}; }}

        .rec-category {{
            color: {TEXT_MUTED};
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 6px;
        }}
        .rec-finding {{
            color: {NVIDIA_WHITE};
            font-size: 15px;
            font-weight: 600;
            margin-bottom: 8px;
            line-height: 1.4;
        }}
        .rec-impact {{
            color: {TEXT_SECONDARY};
            font-size: 13px;
            margin-bottom: 12px;
            line-height: 1.5;
        }}
        .rec-action {{
            color: {NVIDIA_GREEN};
            font-size: 14px;
            font-weight: 500;
            line-height: 1.5;
            padding: 12px;
            background: rgba(118, 185, 0, 0.08);
            border-radius: 6px;
            border: 1px solid rgba(118, 185, 0, 0.2);
        }}
        .rec-savings {{
            color: {TEXT_MUTED};
            font-size: 12px;
            margin-top: 10px;
            font-style: italic;
        }}

        /* --- Data tables --- */
        .stDataFrame {{
            border: 1px solid {CARD_BORDER};
            border-radius: 8px;
        }}

        /* --- Footer --- */
        .nvidia-footer {{
            text-align: center;
            color: {TEXT_MUTED};
            font-size: 12px;
            padding: 32px 0 16px 0;
            margin-top: 48px;
            border-top: 1px solid {CARD_BORDER};
        }}
        .nvidia-footer a {{
            color: {NVIDIA_GREEN};
            text-decoration: none;
        }}

        /* --- Sidebar dark styling --- */
        [data-testid="stSidebar"] {{
            background-color: {NVIDIA_GRAY_950};
            border-right: 1px solid {CARD_BORDER};
        }}
        [data-testid="stSidebar"] .stMarkdown p {{
            color: {TEXT_SECONDARY};
        }}

        /* --- Plotly charts dark bg --- */
        .stPlotlyChart {{
            border: 1px solid {CARD_BORDER};
            border-radius: 8px;
            overflow: hidden;
        }}

        /* --- Download button --- */
        .stDownloadButton > button {{
            background-color: {NVIDIA_GREEN} !important;
            color: {NVIDIA_BLACK} !important;
            font-weight: 600;
            border: none !important;
            border-radius: 6px;
        }}
        .stDownloadButton > button:hover {{
            background-color: {NVIDIA_GREEN_LIGHT} !important;
        }}

        /* --- Selectbox and inputs --- */
        .stSelectbox [data-baseweb="select"] {{
            background-color: {CARD_BG};
            border-color: {CARD_BORDER};
        }}

        /* --- Expander --- */
        .streamlit-expanderHeader {{
            color: {TEXT_PRIMARY} !important;
            background-color: {CARD_BG} !important;
            border: 1px solid {CARD_BORDER};
            border-radius: 8px;
        }}

        /* --- File uploader --- */
        [data-testid="stFileUploader"] {{
            background-color: {CARD_BG};
            border: 1px dashed {CARD_BORDER};
            border-radius: 8px;
            padding: 16px;
        }}

        /* --- Horizontal rule --- */
        hr {{
            border-color: {CARD_BORDER};
        }}

        /* --- Hide Streamlit branding --- */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        header {{visibility: hidden;}}
    </style>
    """


def get_plotly_layout(title="", height=400):
    """Return standard dark Plotly layout matching NVIDIA theme."""
    return dict(
        title=dict(text=title, font=dict(color=TEXT_PRIMARY, size=16, family="Inter")),
        paper_bgcolor=CARD_BG,
        plot_bgcolor=CARD_BG,
        font=dict(color=TEXT_SECONDARY, size=12, family="Inter"),
        height=height,
        margin=dict(l=60, r=30, t=50, b=50),
        xaxis=dict(
            gridcolor=NVIDIA_GRAY_800,
            zerolinecolor=NVIDIA_GRAY_800,
            tickfont=dict(color=TEXT_SECONDARY),
        ),
        yaxis=dict(
            gridcolor=NVIDIA_GRAY_800,
            zerolinecolor=NVIDIA_GRAY_800,
            tickfont=dict(color=TEXT_SECONDARY),
        ),
        legend=dict(
            font=dict(color=TEXT_SECONDARY),
            bgcolor="rgba(0,0,0,0)",
        ),
        hoverlabel=dict(
            bgcolor=NVIDIA_GRAY_900,
            font_size=13,
            font_family="Inter",
            font_color=TEXT_PRIMARY,
        ),
    )
