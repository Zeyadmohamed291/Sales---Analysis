import streamlit as st
import pandas as pd
import os

def load_excel_data():
    """Load the raw Enriched Sales Data for dynamic filtering (optimized)."""
    print("Inside load_excel_data")
    base_dir = os.path.dirname(os.path.dirname(__file__))
    parquet_path = os.path.join(base_dir, "Enriched_Sales_Data.parquet")
    excel_path = os.path.join(base_dir, "Enriched_Sales_Data.xlsx")
    csv_path = os.path.join(base_dir, "Enriched_Sales_Data.csv")
    if os.path.exists(csv_path):
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            df = pd.read_csv(csv_path)
    else:
        df = pd.read_excel(excel_path)
        
    return df

def format_currency(value):
    """Format a number into a compact currency string (e.g., $969.0M, $27.7K)."""
    if pd.isna(value):
        return "$0"
    if value >= 1_000_000:
        return f"${value / 1_000_000:.1f}M"
    elif value >= 1_000:
        return f"${value / 1_000:.1f}K"
    else:
        return f"${value:,.0f}"

def format_number(value):
    """Format a number into a compact string (e.g., 27.7K)."""
    if pd.isna(value):
        return "0"
    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    elif value >= 1_000:
        return f"{value / 1_000:.1f}K"
    else:
        return f"{value:,.0f}"
