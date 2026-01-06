"""
Sales Analytics dashboard page
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.data_loader import get_sales_over_time, load_order_summary

def render():
    """Render sales analytics page"""
    
    st.title("📈 Sales Analytics")
    st.markdown("Detailed sales performance and revenue analysis")
    
    # Date filters - Brazilian E-Commerce data is from 2016-2018
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        start_date = st.date_input(
            "Start Date",
            value=datetime(2016, 1, 1),
            min_value=datetime(2016, 1, 1),
            max_value=datetime(2018, 12, 31)
        )
    
    with col2:
        end_date = st.date_input(
            "End Date",
            value=datetime(2018, 12, 31),
            min_value=datetime(2016, 1, 1),
            max_value=datetime(2018, 12, 31)
        )
    
    with col3:
        granularity = st.selectbox("View By", ["day", "week", "month"])
    
    # Load data
    with st.spinner("Loading sales data..."):
        sales_data = get_sales_over_time(
            start_date.strftime("%Y-%m-%d"),
            end_date.strftime("%Y-%m-%d"),
            granularity
        )
    
    if sales_data.empty:
        st.warning("No data available for selected date range")
        return
    
    # Revenue metrics
    total_revenue = sales_data['REVENUE'].sum()
    total_orders = sales_data['ORDER_COUNT'].sum()
    avg_order_value = sales_data['AVG_ORDER_VALUE'].mean()
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Revenue", f"R$ {total_revenue:,.2f}")
    col2.metric("Total Orders", f"{total_orders:,.0f}")
    col3.metric("Avg Order Value", f"R$ {avg_order_value:,.2f}")
    
    st.markdown("---")
    
    # Revenue trend with moving average
    st.subheader("💰 Revenue Trend")
    
    sales_data['REVENUE_MA7'] = sales_data['REVENUE'].rolling(window=7, min_periods=1).mean()
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=sales_data['DATE'],
        y=sales_data['REVENUE'],
        name='Daily Revenue',
        line=dict(color='lightblue', width=1),
        opacity=0.5
    ))
    fig.add_trace(go.Scatter(
        x=sales_data['DATE'],
        y=sales_data['REVENUE_MA7'],
        name='7-Day Moving Avg',
        line=dict(color='#1f77b4', width=3)
    ))
    fig.update_layout(
        title="Revenue with Moving Average",
        xaxis_title="Date",
        yaxis_title="Revenue (R$)",
        hovermode='x unified',
        height=450
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Orders and AOV comparison
    col1, col2 = st.columns(2)
    
    with col1:
        fig_orders = px.bar(
            sales_data,
            x='DATE',
            y='ORDER_COUNT',
            title='Orders Over Time',
            labels={'ORDER_COUNT': 'Orders', 'DATE': 'Date'},
            color='ORDER_COUNT',
            color_continuous_scale='Blues'
        )
        st.plotly_chart(fig_orders, use_container_width=True)
    
    with col2:
        fig_aov = px.line(
            sales_data,
            x='DATE',
            y='AVG_ORDER_VALUE',
            title='Average Order Value Trend',
            labels={'AVG_ORDER_VALUE': 'AOV (R$)', 'DATE': 'Date'},
            markers=True
        )
        fig_aov.update_traces(line_color='#2ca02c', line_width=2)
        st.plotly_chart(fig_aov, use_container_width=True)
    
    # Load detailed order data
    st.markdown("---")
    st.subheader("📋 Recent Orders")
    
    with st.spinner("Loading order details..."):
        orders = load_order_summary(
            start_date.strftime("%Y-%m-%d"),
            end_date.strftime("%Y-%m-%d")
        )
    
    if not orders.empty:
        # Show summary stats
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Orders", len(orders))
        col2.metric("Delivered", (orders['ORDER_STATUS'] == 'delivered').sum())
        col3.metric("Canceled", (orders['ORDER_STATUS'] == 'canceled').sum())
        col4.metric("In Transit", (orders['ORDER_STATUS'] == 'shipped').sum())
        
        # Show data table
        st.dataframe(
            orders[[
                'ORDER_ID', 'ORDER_PURCHASE_TIMESTAMP', 'ORDER_STATUS',
                'TOTAL_ORDER_VALUE', 'TOTAL_ITEMS', 'REVIEW_SCORE'
            ]].head(100),
            use_container_width=True
        )
        
        # Download button
        csv = orders.to_csv(index=False)
        st.download_button(
            label="📥 Download Full Data",
            data=csv,
            file_name=f"sales_data_{start_date}_{end_date}.csv",
            mime="text/csv"
        )
