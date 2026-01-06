"""
Overview dashboard page - High level KPIs and trends
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.data_loader import (
    get_kpi_metrics,
    get_sales_over_time,
    get_customer_segments,
    get_top_products
)


def render():
    """Render the overview dashboard page"""
    
    st.title("🏠 Business Overview")
    st.markdown("High-level business metrics and trends")
    
    # Date range - Brazilian E-Commerce data is from 2016-2018
    # Use full data range by default
    start_date = "2016-01-01"
    end_date = "2018-12-31"
    
    # Load KPI metrics
    with st.spinner("Loading KPI metrics..."):
        kpis = get_kpi_metrics(start_date, end_date)
    
    if not kpis:
        st.warning("No data available for the selected date range")
        return
    
    # Display KPIs
    st.subheader("📊 Key Performance Indicators")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Orders",
            value=f"{kpis.get('TOTAL_ORDERS', 0) or 0:,.0f}",
            delta=None
        )
        st.metric(
            label="Total Customers",
            value=f"{kpis.get('TOTAL_CUSTOMERS', 0) or 0:,.0f}",
            delta=None
        )
    
    with col2:
        revenue = kpis.get('TOTAL_REVENUE', 0) or 0
        st.metric(
            label="Total Revenue",
            value=f"R$ {revenue:,.2f}",
            delta=None
        )
        avg_order = kpis.get('AVG_ORDER_VALUE', 0) or 0
        st.metric(
            label="Avg Order Value",
            value=f"R$ {avg_order:,.2f}",
            delta=None
        )
    
    with col3:
        avg_delivery = kpis.get('AVG_DELIVERY_DAYS', 0) or 0
        st.metric(
            label="Avg Delivery Days",
            value=f"{avg_delivery:.1f}",
            delta=None
        )
        late_rate = (kpis.get('LATE_DELIVERY_RATE', 0) or 0) * 100
        st.metric(
            label="Late Delivery Rate",
            value=f"{late_rate:.1f}%",
            delta=None,
            delta_color="inverse"
        )
    
    with col4:
        avg_review = kpis.get('AVG_REVIEW_SCORE', 0) or 0
        st.metric(
            label="Avg Review Score",
            value=f"{avg_review:.2f} / 5.0",
            delta=None
        )
        cancel_rate = (kpis.get('CANCELLATION_RATE', 0) or 0) * 100
        st.metric(
            label="Cancellation Rate",
            value=f"{cancel_rate:.1f}%",
            delta=None,
            delta_color="inverse"
        )
    
    st.markdown("---")
    
    # Sales trends
    st.subheader("📈 Sales Trends")
    
    col1, col2 = st.columns([3, 1])
    
    with col2:
        granularity = st.selectbox(
            "Granularity",
            ["day", "week", "month"],
            index=1
        )
    
    with st.spinner("Loading sales trends..."):
        sales_data = get_sales_over_time(start_date, end_date, granularity)
    
    if not sales_data.empty:
        # Revenue trend
        fig_revenue = go.Figure()
        fig_revenue.add_trace(go.Scatter(
            x=sales_data['DATE'],
            y=sales_data['REVENUE'],
            mode='lines+markers',
            name='Revenue',
            line=dict(color='#1f77b4', width=3),
            fill='tozeroy'
        ))
        fig_revenue.update_layout(
            title="Revenue Over Time",
            xaxis_title="Date",
            yaxis_title="Revenue (R$)",
            hovermode='x unified',
            height=400
        )
        st.plotly_chart(fig_revenue, use_container_width=True)
        
        # Orders and customers
        col1, col2 = st.columns(2)
        
        with col1:
            fig_orders = px.line(
                sales_data,
                x='DATE',
                y='ORDER_COUNT',
                title='Orders Over Time',
                labels={'ORDER_COUNT': 'Number of Orders', 'DATE': 'Date'}
            )
            fig_orders.update_traces(line_color='#ff7f0e', line_width=3)
            st.plotly_chart(fig_orders, use_container_width=True)
        
        with col2:
            fig_customers = px.line(
                sales_data,
                x='DATE',
                y='UNIQUE_CUSTOMERS',
                title='Unique Customers Over Time',
                labels={'UNIQUE_CUSTOMERS': 'Customers', 'DATE': 'Date'}
            )
            fig_customers.update_traces(line_color='#2ca02c', line_width=3)
            st.plotly_chart(fig_customers, use_container_width=True)
    else:
        st.info("No sales trend data available")
    
    st.markdown("---")
    
    # Customer segments and top products
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("👥 Customer Segments")
        with st.spinner("Loading customer segments..."):
            segments = get_customer_segments()
        
        if not segments.empty:
            fig_segments = px.pie(
                segments,
                values='CUSTOMER_COUNT',
                names='CUSTOMER_SEGMENT',
                title='Customer Distribution by Segment',
                color_discrete_sequence=px.colors.sequential.Blues_r
            )
            st.plotly_chart(fig_segments, use_container_width=True)
            
            st.dataframe(
                segments[['CUSTOMER_SEGMENT', 'CUSTOMER_COUNT', 'AVG_REVENUE', 'AVG_ORDER_VALUE']],
                use_container_width=True
            )
        else:
            st.info("No customer segment data available")
    
    with col2:
        st.subheader("📦 Top Product Categories")
        with st.spinner("Loading top products..."):
            products = get_top_products(limit=10)
        
        if not products.empty:
            fig_products = px.bar(
                products,
                x='TOTAL_REVENUE',
                y='PRODUCT_CATEGORY',
                orientation='h',
                title='Top 10 Categories by Revenue',
                labels={'TOTAL_REVENUE': 'Revenue (R$)', 'PRODUCT_CATEGORY': 'Category'},
                color='TOTAL_REVENUE',
                color_continuous_scale='Blues'
            )
            fig_products.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig_products, use_container_width=True)
        else:
            st.info("No product data available")
    
    # Refresh button
    st.markdown("---")
    if st.button("🔄 Refresh Data", type="primary"):
        from utils.snowflake_connector import clear_cache
        clear_cache()
        st.rerun()
