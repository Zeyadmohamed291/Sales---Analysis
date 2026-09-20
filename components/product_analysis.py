import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.theme import get_chart_layout, COLORS
from utils.data_loader import format_currency

def render(df):
    if df.empty:
        return
        
    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown("<div class='dash-card'>", unsafe_allow_html=True)
        st.markdown("<div class='card-title'>Revenue by Category</div>", unsafe_allow_html=True)
        st.markdown("<div class='card-subtitle'>Product segment performance</div>", unsafe_allow_html=True)
        
        df_cat = df.groupby('Category')['SalesAmount'].sum().reset_index()
        fig_cat = px.pie(
            df_cat, values="SalesAmount", names="Category", 
            hole=0.7,
            color_discrete_sequence=[COLORS["revenue"], COLORS["profit"], COLORS["orders"]]
        )
        fig_cat.update_traces(textposition='inside', textinfo='percent+label', showlegend=False)
        total_rev = df_cat['SalesAmount'].sum()
        fig_cat.add_annotation(text=f"<b>{format_currency(total_rev)}</b><br><span style='font-size:11px'>Total</span>", 
                               x=0.5, y=0.5, showarrow=False, font=dict(size=18, color=COLORS['text_main']))
        
        layout_cat = get_chart_layout(height=360)
        fig_cat.update_layout(layout_cat)
        st.plotly_chart(fig_cat, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with c2:
        st.markdown("<div class='dash-card'>", unsafe_allow_html=True)
        st.markdown("<div class='card-title'>Cost vs Profit by Subcategory</div>", unsafe_allow_html=True)
        st.markdown("<div class='card-subtitle'>Financial efficiency of product lines</div>", unsafe_allow_html=True)
        
        df_sub = df.groupby('Subcategory').agg({'Profit': 'sum', 'TotalCost': 'sum'}).reset_index()
        df_sub['TotalRevenue'] = df_sub['Profit'] + df_sub['TotalCost']
        df_sub = df_sub.sort_values('TotalRevenue', ascending=False).head(10)
        
        fig_sub = go.Figure()
        fig_sub.add_trace(go.Bar(
            x=df_sub["Subcategory"], y=df_sub["TotalCost"],
            name="Cost", marker_color=COLORS["cost"]
        ))
        fig_sub.add_trace(go.Bar(
            x=df_sub["Subcategory"], y=df_sub["Profit"],
            name="Profit", marker_color=COLORS["profit"]
        ))
        layout_sub = get_chart_layout(height=360)
        layout_sub.update(
            barmode="group", 
            yaxis=dict(title="Amount ($)"),
            showlegend=True, 
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        fig_sub.update_layout(layout_sub)
        st.plotly_chart(fig_sub, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    st.markdown("<div class='dash-card'>", unsafe_allow_html=True)
    st.markdown("<div class='card-title'>Product Performance Matrix</div>", unsafe_allow_html=True)
    st.markdown("<div class='card-subtitle'>Detailed profitability ranking for top 15 products</div>", unsafe_allow_html=True)
    
    df_prod = df.groupby(['ModelName', 'Category', 'Subcategory']).agg({
        'SalesAmount': 'sum',
        'TotalCost': 'sum',
        'Profit': 'sum',
        'Quantity': 'sum'
    }).reset_index()
    
    df_prod['Margin %'] = (df_prod['Profit'] / df_prod['SalesAmount']) * 100
    df_prod = df_prod.sort_values('Profit', ascending=False).head(15)
    
    # Format for display
    display_df = df_prod.copy()
    display_df["SalesAmount"] = display_df["SalesAmount"].apply(lambda x: f"${x:,.0f}")
    display_df["TotalCost"] = display_df["TotalCost"].apply(lambda x: f"${x:,.0f}")
    display_df["Profit"] = display_df["Profit"].apply(lambda x: f"${x:,.0f}")
    display_df["Margin %"] = display_df["Margin %"].apply(lambda x: f"{x:.1f}%")
    
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )
    st.markdown("</div>", unsafe_allow_html=True)
