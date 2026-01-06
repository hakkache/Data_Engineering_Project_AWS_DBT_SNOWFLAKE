"""
Customer Analytics dashboard page
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.data_loader import load_customer_features, get_customer_segments


def render():
    """Render customer analytics page"""
    
    st.title("👥 Customer Analytics")
    st.markdown("Customer behavior, segmentation, and lifetime value analysis")
    
    # Load customer data
    with st.spinner("Loading customer data..."):
        customers = load_customer_features()
        segments = get_customer_segments()
    
    if customers.empty:
        st.warning("No customer data available")
        return
    
    # Customer KPIs
    st.subheader("📊 Customer Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_customers = len(customers)
    avg_clv = customers['CUSTOMER_LIFETIME_VALUE'].mean()
    avg_orders = customers['CUSTOMER_ORDER_COUNT'].mean()
    
    col1.metric("Total Customers", f"{total_customers:,}")
    col2.metric("Avg Customer LTV", f"R$ {avg_clv:,.2f}")
    col3.metric("Avg Orders per Customer", f"{avg_orders:.1f}")
    col4.metric("Avg Tenure Days", f"{customers['CUSTOMER_TENURE_DAYS'].mean():.0f}")
    
    st.markdown("---")
    
    # Customer segmentation
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("🎯 Customer Segmentation")
        
        if not segments.empty:
            fig_segments = px.pie(
                segments,
                values='CUSTOMER_COUNT',
                names='CUSTOMER_SEGMENT',
                title='Customer Distribution',
                hole=0.4,
                color_discrete_sequence=px.colors.sequential.Blues_r
            )
            fig_segments.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_segments, use_container_width=True)
            
            st.dataframe(segments, use_container_width=True)
    
    with col2:
        st.subheader("💰 Revenue by Segment")
        
        if not segments.empty:
            fig_revenue = px.bar(
                segments,
                x='CUSTOMER_SEGMENT',
                y='AVG_REVENUE',
                title='Average Revenue per Customer',
                color='AVG_REVENUE',
                color_continuous_scale='Blues',
                labels={'AVG_REVENUE': 'Avg Revenue (R$)', 'CUSTOMER_SEGMENT': 'Segment'}
            )
            st.plotly_chart(fig_revenue, use_container_width=True)
    
    st.markdown("---")
    
    # Customer lifetime value distribution
    st.subheader("📈 Customer Lifetime Value Distribution")
    
    fig_clv = px.histogram(
        customers,
        x='CUSTOMER_LIFETIME_VALUE',
        nbins=50,
        title='CLV Distribution',
        labels={'CUSTOMER_LIFETIME_VALUE': 'Customer Lifetime Value (R$)'},
        color_discrete_sequence=['#1f77b4']
    )
    fig_clv.update_layout(showlegend=False, height=400)
    st.plotly_chart(fig_clv, use_container_width=True)
    
    # Top customers
    st.markdown("---")
    st.subheader("⭐ Top 20 Customers by Revenue")
    
    top_customers = customers.nlargest(20, 'CUSTOMER_LIFETIME_VALUE')
    
    fig_top = px.bar(
        top_customers,
        x='CUSTOMER_LIFETIME_VALUE',
        y='CUSTOMER_ID',
        orientation='h',
        title='Top 20 Customers',
        labels={'CUSTOMER_LIFETIME_VALUE': 'Total Revenue (R$)', 'CUSTOMER_ID': 'Customer ID'},
        color='CUSTOMER_LIFETIME_VALUE',
        color_continuous_scale='Blues'
    )
    fig_top.update_layout(height=600, showlegend=False)
    st.plotly_chart(fig_top, use_container_width=True)
    
    # Customer behavior metrics
    st.markdown("---")
    st.subheader("🔍 Customer Behavior Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_orders = px.scatter(
            customers.sample(min(1000, len(customers))),
            x='CUSTOMER_ORDER_COUNT',
            y='CUSTOMER_LIFETIME_VALUE',
            title='Orders vs Revenue',
            labels={'CUSTOMER_ORDER_COUNT': 'Total Orders', 'CUSTOMER_LIFETIME_VALUE': 'Total Revenue (R$)'},
            color='CUSTOMER_AVG_ORDER_VALUE',
            color_continuous_scale='RdYlGn',
            opacity=0.6
        )
        st.plotly_chart(fig_orders, use_container_width=True)
    
    with col2:
        fig_tenure = px.histogram(
            customers,
            x='CUSTOMER_TENURE_DAYS',
            nbins=30,
            title='Customer Tenure Distribution',
            labels={'CUSTOMER_TENURE_DAYS': 'Customer Tenure (Days)'},
            color_discrete_sequence=['#ff7f0e']
        )
        st.plotly_chart(fig_tenure, use_container_width=True)
    
    # Geographic analysis
    st.markdown("---")
    st.subheader("🗺️ Geographic Distribution")
    
    state_stats = customers.groupby('CUSTOMER_STATE').agg({
        'CUSTOMER_ID': 'count',
        'CUSTOMER_LIFETIME_VALUE': 'sum'
    }).reset_index()
    state_stats.columns = ['STATE', 'CUSTOMER_COUNT', 'TOTAL_REVENUE']
    state_stats = state_stats.sort_values('TOTAL_REVENUE', ascending=False).head(15)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_state_customers = px.bar(
            state_stats,
            x='STATE',
            y='CUSTOMER_COUNT',
            title='Customers by State (Top 15)',
            color='CUSTOMER_COUNT',
            color_continuous_scale='Blues'
        )
        st.plotly_chart(fig_state_customers, use_container_width=True)
    
    with col2:
        fig_state_revenue = px.bar(
            state_stats,
            x='STATE',
            y='TOTAL_REVENUE',
            title='Revenue by State (Top 15)',
            color='TOTAL_REVENUE',
            color_continuous_scale='Greens'
        )
        st.plotly_chart(fig_state_revenue, use_container_width=True)
    
    # Download button
    st.markdown("---")
    csv = customers.to_csv(index=False)
    st.download_button(
        label="📥 Download Customer Data",
        data=csv,
        file_name="customer_analytics.csv",
        mime="text/csv"
    )
