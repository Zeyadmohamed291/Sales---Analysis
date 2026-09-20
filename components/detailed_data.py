import streamlit as st
import pandas as pd
from utils.theme import COLORS

def render(df):
    if df.empty:
        return
        
    st.markdown("<div class='dash-card'>", unsafe_allow_html=True)
    st.markdown("<div class='card-title'>Data Explorer</div>", unsafe_allow_html=True)
    st.markdown("<div class='card-subtitle'>View, filter, and export the underlying analytics dataset</div>", unsafe_allow_html=True)
    
    # Define business-friendly columns
    display_columns = [
        'SalesOrderNumber', 'OrderDate', 'CustomerName', 'Region', 
        'Category', 'Subcategory', 'ModelName', 
        'Quantity', 'SalesAmount', 'TotalCost', 'Profit'
    ]
    
    # Ensure columns exist before filtering
    available_cols = [c for c in display_columns if c in df.columns]
    display_df = df[available_cols].copy()
    
    # Ensure dates look clean
    if 'OrderDate' in display_df.columns:
        display_df['OrderDate'] = display_df['OrderDate'].astype(str).str[:10]
        
    st.dataframe(
        display_df.head(1000), 
        use_container_width=True, 
        hide_index=True,
        height=600
    )
    
    st.caption("Note: For performance reasons, the table above previews the first 1,000 rows. Use the 'Download CSV' button to access the full dataset.")
    
    # Download button for filtered data
    csv = display_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Filtered Data (CSV)",
        data=csv,
        file_name='filtered_sales_data.csv',
        mime='text/csv',
    )
    
    st.markdown("</div>", unsafe_allow_html=True)
