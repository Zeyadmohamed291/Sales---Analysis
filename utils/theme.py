import streamlit as st

# Define consistent premium brand colors (SaaS/Executive BI style)
COLORS = {
    "revenue": "#38bdf8",     # Electric Blue
    "profit": "#10b981",      # Emerald Green
    "cost": "#f59e0b",        # Amber/Orange (changed from red per requirements)
    "negative": "#ef4444",    # Red
    "orders": "#a855f7",      # Purple
    "customers": "#22d3ee",   # Cyan
    "primary": "#38bdf8",
    "secondary": "#94a3b8",
    "background_main": "#07111F",
    "background_card": "#0B1424",
    "background_card_alt": "#0E1B2D",
    "border": "rgba(255, 255, 255, 0.05)",
    "text_main": "#f8fafc",
    "text_muted": "#64748b"
}

def apply_custom_css():
    """Applies the global custom CSS for the premium dark navy theme."""
    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        /* Global Font & Main Background */
        html, body, [class*="css"] {{
            font-family: 'Inter', sans-serif !important;
        }}
        .stApp {{
            background-color: {COLORS['background_main']} !important;
        }}
        
        /* Hide Streamlit Defaults */
        #MainMenu {{visibility: hidden;}}
        header {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        .stDeployButton {{display:none;}}
        
        /* Reduce Default Padding */
        .block-container {{
            padding-top: 2rem !important;
            padding-bottom: 2rem !important;
            padding-left: 3rem !important;
            padding-right: 3rem !important;
            max-width: 100% !important;
        }}
        
        /* Sidebar Premium Styling */
        [data-testid="stSidebar"] {{
            background-color: {COLORS['background_card']} !important;
            border-right: 1px solid {COLORS['border']} !important;
        }}
        
        /* Widget Styling (Multiselect, Selectbox) */
        .stMultiSelect div[data-baseweb="select"] {{
            background-color: {COLORS['background_card_alt']} !important;
            border: 1px solid {COLORS['border']} !important;
            border-radius: 6px !important;
        }}
        .stMultiSelect span[data-baseweb="tag"] {{
            background-color: rgba(56, 189, 248, 0.15) !important; /* Subtle blue */
            color: #38bdf8 !important;
            border-radius: 4px;
        }}
        
        /* Custom KPI Card Styling */
        .kpi-card {{
            background-color: {COLORS['background_card']};
            border: 1px solid {COLORS['border']};
            border-radius: 8px;
            padding: 16px 20px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            height: 100%;
            min-height: 120px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }}
        .kpi-title {{
            color: {COLORS['text_muted']};
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 4px;
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        .kpi-value {{
            color: {COLORS['text_main']};
            font-size: 28px;
            font-weight: 700;
            line-height: 1.2;
            margin-bottom: 4px;
        }}
        .kpi-sub {{
            color: {COLORS['text_muted']};
            font-size: 12px;
        }}
        
        /* Generic Dashboard Card (for charts) */
        .dash-card {{
            background-color: {COLORS['background_card']};
            border: 1px solid {COLORS['border']};
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            height: 100%;
        }}
        .card-title {{
            font-size: 16px;
            font-weight: 600;
            color: {COLORS['text_main']};
            margin-bottom: 4px;
        }}
        .card-subtitle {{
            font-size: 13px;
            color: {COLORS['text_muted']};
            margin-bottom: 16px;
        }}
        
        /* Insights Card */
        .insight-item {{
            display: flex;
            align-items: flex-start;
            gap: 12px;
            margin-bottom: 16px;
            padding-bottom: 12px;
            border-bottom: 1px solid {COLORS['border']};
        }}
        .insight-item:last-child {{
            border-bottom: none;
            margin-bottom: 0;
            padding-bottom: 0;
        }}
        .insight-icon {{
            font-size: 18px;
            margin-top: 2px;
        }}
        .insight-text {{
            display: flex;
            flex-direction: column;
        }}
        .insight-main {{
            color: {COLORS['text_main']};
            font-size: 14px;
            font-weight: 600;
        }}
        .insight-sub {{
            color: {COLORS['primary']};
            font-size: 13px;
            font-weight: 500;
        }}
        
        /* Radio Buttons (for navigation) */
        div[role="radiogroup"] label {{
            background-color: transparent !important;
            border-radius: 6px;
            padding: 8px 12px;
            margin-bottom: 4px;
            transition: all 0.2s ease;
        }}
        div[role="radiogroup"] label:hover {{
            background-color: rgba(255,255,255,0.02) !important;
        }}
        /* Very tricky to style Streamlit native radio active state via CSS cleanly, 
           we rely on default Streamlit logic but subdued */
           
    </style>
    """, unsafe_allow_html=True)

def get_chart_layout(title="", height=320):
    """Returns a standardized premium Plotly layout dictionary."""
    return dict(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=10, b=10), # Minimal margins, rely on the HTML card padding
        font=dict(family="Inter", color=COLORS['text_muted'], size=12),
        xaxis=dict(
            showgrid=False, 
            zeroline=False, 
            showline=False,
            fixedrange=True # Prevent accidental zooming
        ),
        yaxis=dict(
            showgrid=True, 
            gridcolor=COLORS['border'], 
            zeroline=False,
            fixedrange=True
        ),
        hoverlabel=dict(
            bgcolor=COLORS['background_card_alt'], 
            font_size=13, 
            font_family="Inter",
            bordercolor=COLORS['border']
        ),
        showlegend=False
    )
