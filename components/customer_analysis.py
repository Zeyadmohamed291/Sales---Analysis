import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.theme import get_chart_layout, COLORS
from utils.data_loader import format_currency

def render(df):
    if df.empty:
        return
        
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.markdown("<div class='dash-card'>", unsafe_allow_html=True)
        st.markdown("<div class='card-title'>Revenue by Gender</div>", unsafe_allow_html=True)
        st.markdown("<div class='card-subtitle'>Demographic distribution</div>", unsafe_allow_html=True)
        
        df_g = df.groupby('Gender')['SalesAmount'].sum().reset_index()
        df_g['Gender'] = df_g['Gender'].map({'M': 'Male', 'F': 'Female'})
        
        fig_g = px.pie(
            df_g, values="SalesAmount", names="Gender", 
            hole=0.7,
            color_discrete_sequence=["#f472b6", COLORS["revenue"]] # Pink for Female, Blue for Male
        )
        fig_g.update_traces(textposition='inside', textinfo='percent+label', showlegend=False)
        total_rev = df_g['SalesAmount'].sum()
        fig_g.add_annotation(text=f"<b>{format_currency(total_rev)}</b>", 
                               x=0.5, y=0.5, showarrow=False, font=dict(size=18, color=COLORS['text_main']))
        
        layout_g = get_chart_layout(height=320)
        fig_g.update_layout(layout_g)
        st.plotly_chart(fig_g, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with c2:
        st.markdown("<div class='dash-card'>", unsafe_allow_html=True)
        st.markdown("<div class='card-title'>Revenue by Education</div>", unsafe_allow_html=True)
        st.markdown("<div class='card-subtitle'>Customer education levels</div>", unsafe_allow_html=True)
        
        df_edu = df.groupby('Education')['SalesAmount'].sum().reset_index().sort_values('SalesAmount', ascending=True)
        
        fig_edu = px.bar(
            df_edu, x="SalesAmount", y="Education", orientation='h',
            color_discrete_sequence=[COLORS["secondary"]]
        )
        fig_edu.update_traces(texttemplate='%{x:$.2s}', textposition='outside')
        layout_edu = get_chart_layout(height=320)
        layout_edu.update(xaxis=dict(title=""), yaxis=dict(title=""))
        fig_edu.update_layout(layout_edu)
        st.plotly_chart(fig_edu, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with c3:
        st.markdown("<div class='dash-card'>", unsafe_allow_html=True)
        st.markdown("<div class='card-title'>Revenue by Age Group</div>", unsafe_allow_html=True)
        st.markdown("<div class='card-subtitle'>Generational purchasing power</div>", unsafe_allow_html=True)
        
        df_age = df.groupby('AgeGroup')['SalesAmount'].sum().reset_index()
        # Sort age groups logically if possible
        age_order = ['<25', '25-34', '35-44', '45-54', '55-64', '65+']
        df_age['AgeGroup'] = pd.Categorical(df_age['AgeGroup'], categories=age_order, ordered=True)
        df_age = df_age.sort_values('AgeGroup')
        
        fig_age = go.Figure()
        fig_age.add_trace(go.Scatter(
            x=df_age["AgeGroup"], y=df_age["SalesAmount"],
            mode="lines+markers",
            line=dict(color=COLORS["customers"], width=3, shape="spline"),
            fill='tozeroy', fillcolor='rgba(34, 211, 238, 0.1)',
            marker=dict(size=8, color=COLORS["text_main"])
        ))
        layout_age = get_chart_layout(height=320)
        layout_age.update(xaxis=dict(title=""), yaxis=dict(title=""))
        fig_age.update_layout(layout_age)
        st.plotly_chart(fig_age, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    st.markdown("<div class='dash-card'>", unsafe_allow_html=True)
    st.markdown("<div class='card-title'>Top 10 High-Value Customers</div>", unsafe_allow_html=True)
    st.markdown("<div class='card-subtitle'>Most profitable individual accounts</div>", unsafe_allow_html=True)
    
    df_cust = df.groupby(['CustomerKey', 'CustomerName', 'Region']).agg({
        'SalesOrderNumber': 'nunique',
        'SalesAmount': 'sum',
        'Profit': 'sum'
    }).reset_index()
    
    df_cust = df_cust.sort_values('Profit', ascending=False).head(10)
    df_cust.rename(columns={'SalesOrderNumber': 'Orders'}, inplace=True)
    
    display_df = df_cust[['CustomerName', 'Region', 'Orders', 'SalesAmount', 'Profit']].copy()
    display_df["SalesAmount"] = display_df["SalesAmount"].map(lambda x: f"${x:,.2f}")
    display_df["Profit"] = display_df["Profit"].map(lambda x: f"${x:,.2f}")
    
    st.dataframe(
        display_df.head(500),
        use_container_width=True,
        hide_index=True
    )
    st.markdown("</div>", unsafe_allow_html=True)
