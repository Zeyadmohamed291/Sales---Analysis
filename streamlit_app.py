import streamlit as st
import pandas as pd
from datetime import datetime
from utils.theme import apply_custom_css
from utils.data_loader import load_excel_data
from components import (
    executive_overview,
    sales_performance,
    product_analysis,
    customer_analysis,
    geographic_analysis,
    detailed_data
)

# Page Configuration
st.set_page_config(
    page_title="Sales Analytics",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply global premium styling
apply_custom_css()

# Load Data (Raw Enriched Sales Data)
df = load_excel_data()

# ==========================================
# SIDEBAR NAVIGATION & GLOBAL FILTERS
# ==========================================
with st.sidebar:
    # Brand / Logo area
    st.markdown("""
        <div style='display: flex; align-items: center; gap: 10px; margin-bottom: 20px;'>
            <div style='width: 32px; height: 32px; background: #38bdf8; border-radius: 6px; display: flex; justify-content: center; align-items: center; font-weight: bold; color: #fff;'>SA</div>
            <div style='font-size: 18px; font-weight: 600; color: #f8fafc;'>Sales Analytics</div>
        </div>
    """, unsafe_allow_html=True)
    
    selected_page = st.radio(
        "Navigation",
        [
            "Executive Overview",
            "Sales Performance",
            "Product & Category",
            "Customer & Demographics",
            "Geographic Analysis",
            "Detailed Data"
        ],
        label_visibility="collapsed"
    )
    
    st.markdown("<hr style='border-color: rgba(255,255,255,0.05); margin: 20px 0;'>", unsafe_allow_html=True)
    st.markdown("<div style='font-size: 11px; font-weight: 600; color: #64748b; letter-spacing: 1px; margin-bottom: 10px;'>GLOBAL FILTERS</div>", unsafe_allow_html=True)
    
    # Date Filters
    available_years = sorted(df['Year'].dropna().unique().tolist())
    years = st.multiselect("Year", options=available_years, default=[], key="filter_year")
    
    # Geography Filters
    available_regions = sorted(df['Region'].dropna().unique().tolist())
    regions = st.multiselect("Country / Region", options=available_regions, default=[], key="filter_region")
    
    # Product Filters
    available_categories = sorted(df['Category'].dropna().unique().tolist())
    categories = st.multiselect("Product Category", options=available_categories, default=[], key="filter_category")
    
    # Sales Filters
    available_supervisors = sorted(df['SupervisorName'].dropna().unique().tolist())
    supervisors = st.multiselect("Supervisor", options=available_supervisors, default=[], key="filter_supervisor")
    
    # Customer Filters
    available_genders = sorted(df['Gender'].dropna().unique().tolist())
    genders = st.multiselect("Customer Gender", options=available_genders, default=[], format_func=lambda x: "Male" if x == 'M' else ("Female" if x == 'F' else x), key="filter_gender")
    
    if st.button("Reset Filters"):
        st.session_state["filter_year"] = []
        st.session_state["filter_region"] = []
        st.session_state["filter_category"] = []
        st.session_state["filter_supervisor"] = []
        st.session_state["filter_gender"] = []
        st.rerun()

# ==========================================
# APPLY GLOBAL FILTERS
# ==========================================
filtered_df = df.copy()

if years:
    filtered_df = filtered_df[filtered_df['Year'].isin(years)]
if regions:
    filtered_df = filtered_df[filtered_df['Region'].isin(regions)]
if categories:
    filtered_df = filtered_df[filtered_df['Category'].isin(categories)]
if supervisors:
    filtered_df = filtered_df[filtered_df['SupervisorName'].isin(supervisors)]
if genders:
    filtered_df = filtered_df[filtered_df['Gender'].isin(genders)]

# ==========================================
# HEADER
# ==========================================
# Header Area
c1, c2 = st.columns([3, 1])
with c1:
    st.markdown(f"""
        <div style='margin-bottom: 24px;'>
            <h1 style='font-size: 24px; font-weight: 700; color: #f8fafc; margin: 0; padding: 0;'>{selected_page}</h1>
            <div style='font-size: 14px; color: #94a3b8; margin-top: 4px;'>Advanced Sales, Profit & Customer Analytics</div>
        </div>
    """, unsafe_allow_html=True)
with c2:
    import datetime
    
    def format_date_str(d_str):
        if pd.isna(d_str) or not d_str: return "N/A"
        try:
            return datetime.datetime.strptime(str(d_str)[:10], '%Y-%m-%d').strftime('%b %Y')
        except:
            return str(d_str)[:10]

    min_date = format_date_str(filtered_df['OrderDate'].min()) if not filtered_df.empty else "N/A"
    max_date = format_date_str(filtered_df['OrderDate'].max()) if not filtered_df.empty else "N/A"
    st.markdown(f"""
        <div style='text-align: right; margin-top: 8px;'>
            <div style='font-size: 12px; color: #64748b;'>Data Period</div>
            <div style='font-size: 13px; font-weight: 600; color: #e2e8f0;'>{min_date} — {max_date}</div>
            <div style='font-size: 11px; color: #64748b; margin-top: 4px;'>Last Updated: Today</div>
        </div>
    """, unsafe_allow_html=True)

# ==========================================
# MAIN CONTENT ROUTING
# ==========================================
if filtered_df.empty:
    st.warning("No data available for the selected filters. Please adjust your criteria.")
else:
    if selected_page == "Executive Overview":
        executive_overview.render(filtered_df)
    elif selected_page == "Sales Performance":
        sales_performance.render(filtered_df)
    elif selected_page == "Product & Category":
        product_analysis.render(filtered_df)
    elif selected_page == "Customer & Demographics":
        customer_analysis.render(filtered_df)
    elif selected_page == "Geographic Analysis":
        geographic_analysis.render(filtered_df)
    elif selected_page == "Detailed Data":
        detailed_data.render(filtered_df)
