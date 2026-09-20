import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from utils.theme import get_chart_layout, COLORS
from utils.data_loader import format_currency, format_number

def render(df):
    if df.empty:
        return
        
    # --- KPI Calculations ---
    total_revenue = df['SalesAmount'].sum()
    total_profit = df['Profit'].sum()
    total_cost = df['TotalCost'].sum()
    total_orders = df['SalesOrderNumber'].nunique()
    total_customers = df['CustomerKey'].nunique()
    aov = total_revenue / total_orders if total_orders > 0 else 0
    margin = (total_profit / total_revenue) * 100 if total_revenue > 0 else 0

    # --- KPI ROW (6 Cards) ---
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    
    with c1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Total Sales</div>
            <div class="kpi-value">{format_currency(total_revenue)}</div>
            <div class="kpi-sub" style="color: {COLORS['revenue']}">{format_number(df['Quantity'].sum())} Units</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Total Profit</div>
            <div class="kpi-value">{format_currency(total_profit)}</div>
            <div class="kpi-sub" style="color: {COLORS['profit']}">Margin: {margin:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Total Cost</div>
            <div class="kpi-value">{format_currency(total_cost)}</div>
            <div class="kpi-sub" style="color: {COLORS['cost']}">Operations</div>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Total Orders</div>
            <div class="kpi-value">{format_number(total_orders)}</div>
            <div class="kpi-sub" style="color: {COLORS['orders']}">Distinct Transactions</div>
        </div>
        """, unsafe_allow_html=True)
    with c5:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Total Customers</div>
            <div class="kpi-value">{format_number(total_customers)}</div>
            <div class="kpi-sub" style="color: {COLORS['customers']}">Distinct Accounts</div>
        </div>
        """, unsafe_allow_html=True)
    with c6:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Avg Order Value</div>
            <div class="kpi-value">{format_currency(aov)}</div>
            <div class="kpi-sub" style="color: {COLORS['text_muted']}">Per Transaction</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)
    
    # --- ROW 2: MAIN TREND (65%) + KEY INSIGHTS (35%) ---
    r2c1, r2c2 = st.columns([65, 35])
    
    with r2c1:
        st.markdown("<div class='dash-card'>", unsafe_allow_html=True)
        st.markdown("<div class='card-title'>Sales & Profit Trend</div>", unsafe_allow_html=True)
        st.markdown("<div class='card-subtitle'>Quarterly sales and profit performance</div>", unsafe_allow_html=True)
        
        df_trend = df.groupby('YearQuarter').agg({
            'SalesAmount': 'sum',
            'Profit': 'sum'
        }).reset_index()
        df_trend = df_trend.sort_values('YearQuarter')
        
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(
            x=df_trend['YearQuarter'], y=df_trend['SalesAmount'],
            mode='lines', name='Sales',
            line=dict(color=COLORS['revenue'], width=3, shape='spline'),
            fill='tozeroy', fillcolor='rgba(56, 189, 248, 0.05)'
        ))
        fig_trend.add_trace(go.Scatter(
            x=df_trend['YearQuarter'], y=df_trend['Profit'],
            mode='lines', name='Profit',
            line=dict(color=COLORS['profit'], width=2, shape='spline')
        ))
        
        layout = get_chart_layout(height=380)
        layout.update(
            hovermode='x unified',
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        fig_trend.update_layout(layout)
        st.plotly_chart(fig_trend, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with r2c2:
        st.markdown("<div class='dash-card'>", unsafe_allow_html=True)
        st.markdown("<div class='card-title'>Key Insights</div>", unsafe_allow_html=True)
        st.markdown("<div class='card-subtitle'>Data-driven observations</div>", unsafe_allow_html=True)
        
        # Dynamic Insights Logic
        # 1. Top Quarter
        if not df_trend.empty:
            top_q = df_trend.loc[df_trend['SalesAmount'].idxmax()]
            i1 = f"Sales peaked in {top_q['YearQuarter']}"
            i1_sub = f"Reached {format_currency(top_q['SalesAmount'])}"
        else:
            i1, i1_sub = "No trend data", ""
            
        # 2. Top Region
        df_reg = df.groupby('Region')['SalesAmount'].sum().reset_index()
        if not df_reg.empty:
            top_r = df_reg.loc[df_reg['SalesAmount'].idxmax()]
            i2 = f"{top_r['Region']} leads revenue"
            i2_sub = f"Generated {format_currency(top_r['SalesAmount'])}"
        else:
            i2, i2_sub = "No region data", ""
            
        # 3. Top Category
        df_cat = df.groupby('Category')['SalesAmount'].sum().reset_index()
        if not df_cat.empty:
            top_c = df_cat.loc[df_cat['SalesAmount'].idxmax()]
            cat_pct = (top_c['SalesAmount'] / total_revenue) * 100 if total_revenue > 0 else 0
            i3 = f"{top_c['Category']} is leading category"
            i3_sub = f"Contributed {cat_pct:.1f}% of total sales"
        else:
            i3, i3_sub = "No category data", ""
            
        # 4. Top Gender
        df_g = df.groupby('Gender')['SalesAmount'].sum().reset_index()
        if not df_g.empty:
            top_g = df_g.loc[df_g['SalesAmount'].idxmax()]
            g_str = "Male" if top_g['Gender'] == 'M' else "Female"
            i4 = f"{g_str} customer segment"
            i4_sub = f"Contributed {format_currency(top_g['SalesAmount'])}"
        else:
            i4, i4_sub = "No demographic data", ""
            
        st.markdown(f"""
        <div style="margin-top: 24px;">
            <div class="insight-item">
                <div class="insight-icon">📈</div>
                <div class="insight-text">
                    <span class="insight-main">{i1}</span>
                    <span class="insight-sub">{i1_sub}</span>
                </div>
            </div>
            <div class="insight-item">
                <div class="insight-icon">🌎</div>
                <div class="insight-text">
                    <span class="insight-main">{i2}</span>
                    <span class="insight-sub" style="color: {COLORS['profit']};">{i2_sub}</span>
                </div>
            </div>
            <div class="insight-item">
                <div class="insight-icon">📦</div>
                <div class="insight-text">
                    <span class="insight-main">{i3}</span>
                    <span class="insight-sub" style="color: {COLORS['orders']};">{i3_sub}</span>
                </div>
            </div>
            <div class="insight-item">
                <div class="insight-icon">👥</div>
                <div class="insight-text">
                    <span class="insight-main">{i4}</span>
                    <span class="insight-sub" style="color: {COLORS['customers']};">{i4_sub}</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # --- ROW 3: SECONDARY ANALYTICS GRID (3 cols) ---
    r3c1, r3c2, r3c3 = st.columns(3)
    
    with r3c1:
        st.markdown("<div class='dash-card'>", unsafe_allow_html=True)
        st.markdown("<div class='card-title'>Sales by Region</div>", unsafe_allow_html=True)
        st.markdown("<div class='card-subtitle'>Top markets by revenue</div>", unsafe_allow_html=True)
        
        df_reg_bar = df.groupby('Region')['SalesAmount'].sum().reset_index().sort_values('SalesAmount', ascending=True).tail(10)
        fig_reg = px.bar(df_reg_bar, x='SalesAmount', y='Region', orientation='h')
        fig_reg.update_traces(marker_color=COLORS['revenue'], texttemplate='%{x:$.2s}', textposition='outside')
        fig_reg.update_layout(get_chart_layout(height=280))
        st.plotly_chart(fig_reg, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with r3c2:
        st.markdown("<div class='dash-card'>", unsafe_allow_html=True)
        st.markdown("<div class='card-title'>Sales by Category</div>", unsafe_allow_html=True)
        st.markdown("<div class='card-subtitle'>Revenue distribution</div>", unsafe_allow_html=True)
        
        fig_cat = px.pie(df_cat, values='SalesAmount', names='Category', hole=0.75, 
                         color_discrete_sequence=[COLORS['revenue'], COLORS['profit'], COLORS['orders']])
        fig_cat.update_traces(textposition='inside', textinfo='percent+label', showlegend=False)
        fig_cat.add_annotation(text=f"<b>{format_currency(total_revenue)}</b><br><span style='font-size:11px'>Total Sales</span>", 
                               x=0.5, y=0.5, showarrow=False, font=dict(size=18, color=COLORS['text_main']))
        fig_cat.update_layout(get_chart_layout(height=280))
        st.plotly_chart(fig_cat, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with r3c3:
        st.markdown("<div class='dash-card'>", unsafe_allow_html=True)
        st.markdown("<div class='card-title'>Purchase Reasons by Gender</div>", unsafe_allow_html=True)
        st.markdown("<div class='card-subtitle'>Top drivers compared</div>", unsafe_allow_html=True)
        
        df_reas = df.groupby(['SalesReasonName', 'Gender'])['SalesAmount'].sum().reset_index()
        # Get top 4 reasons overall
        top_reasons = df.groupby('SalesReasonName')['SalesAmount'].sum().nlargest(4).index
        df_reas = df_reas[df_reas['SalesReasonName'].isin(top_reasons)]
        
        # Format gender for legend
        df_reas['Gender'] = df_reas['Gender'].map({'M': 'Male', 'F': 'Female'})
        
        fig_reas = px.bar(df_reas, x='SalesReasonName', y='SalesAmount', color='Gender', barmode='group',
                          color_discrete_map={'Male': COLORS['revenue'], 'Female': '#f472b6'}) # Custom pink for female per reqs
        fig_reas.update_layout(get_chart_layout(height=280))
        fig_reas.update_layout(showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, title=""))
        st.plotly_chart(fig_reas, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
