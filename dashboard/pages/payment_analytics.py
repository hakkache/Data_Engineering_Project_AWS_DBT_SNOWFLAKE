"""
Payment Analytics dashboard page
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.data_loader import load_gold_obt_summary


def render():
    """Render payment analytics page"""
    
    st.title("💰 Payment Analytics")
    st.markdown("Payment methods, installments, and transaction analysis")
    
    # Load data
    with st.spinner("Loading payment data..."):
        obt_data = load_gold_obt_summary(limit=10000)
    
    if obt_data.empty or 'PAYMENT_TYPE' not in obt_data.columns:
        st.warning("No payment data available")
        return
    
    # Payment KPIs
    st.subheader("📊 Payment Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_transactions = len(obt_data)
    total_value = obt_data['PAYMENT_VALUE'].sum()
    avg_transaction = obt_data['PAYMENT_VALUE'].mean()
    avg_installments = obt_data['PAYMENT_INSTALLMENTS'].mean()
    
    col1.metric("Total Transactions", f"{total_transactions:,}")
    col2.metric("Total Payment Value", f"R$ {total_value:,.2f}")
    col3.metric("Avg Transaction", f"R$ {avg_transaction:,.2f}")
    col4.metric("Avg Installments", f"{avg_installments:.1f}x")
    
    st.markdown("---")
    
    # Payment type distribution
    st.subheader("💳 Payment Method Distribution")
    
    payment_dist = obt_data.groupby('PAYMENT_TYPE').agg({
        'ORDER_ID': 'count',
        'PAYMENT_VALUE': 'sum'
    }).reset_index()
    payment_dist.columns = ['PAYMENT_TYPE', 'TRANSACTION_COUNT', 'TOTAL_VALUE']
    payment_dist = payment_dist.sort_values('TOTAL_VALUE', ascending=False)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_payment_count = px.pie(
            payment_dist,
            values='TRANSACTION_COUNT',
            names='PAYMENT_TYPE',
            title='Transaction Count by Payment Type',
            hole=0.4,
            color_discrete_sequence=px.colors.sequential.Blues_r
        )
        fig_payment_count.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_payment_count, use_container_width=True)
    
    with col2:
        fig_payment_value = px.pie(
            payment_dist,
            values='TOTAL_VALUE',
            names='PAYMENT_TYPE',
            title='Payment Value by Payment Type',
            hole=0.4,
            color_discrete_sequence=px.colors.sequential.Greens_r
        )
        fig_payment_value.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_payment_value, use_container_width=True)
    
    # Payment type comparison
    st.markdown("---")
    st.subheader("📊 Payment Type Analysis")
    
    fig_payment_bar = px.bar(
        payment_dist,
        x='PAYMENT_TYPE',
        y=['TRANSACTION_COUNT', 'TOTAL_VALUE'],
        title='Payment Type Comparison',
        barmode='group',
        labels={'value': 'Amount', 'variable': 'Metric', 'PAYMENT_TYPE': 'Payment Type'}
    )
    st.plotly_chart(fig_payment_bar, use_container_width=True)
    
    # Installment analysis
    st.markdown("---")
    st.subheader("📅 Installment Analysis")
    
    installment_data = obt_data[obt_data['PAYMENT_INSTALLMENTS'] > 0]
    
    col1, col2 = st.columns(2)
    
    with col1:
        installment_dist = installment_data.groupby('PAYMENT_INSTALLMENTS').size().reset_index()
        installment_dist.columns = ['INSTALLMENTS', 'COUNT']
        installment_dist = installment_dist.sort_values('INSTALLMENTS')
        
        fig_installments = px.bar(
            installment_dist,
            x='INSTALLMENTS',
            y='COUNT',
            title='Distribution of Payment Installments',
            labels={'INSTALLMENTS': 'Number of Installments', 'COUNT': 'Transaction Count'},
            color='COUNT',
            color_continuous_scale='Blues'
        )
        fig_installments.update_layout(showlegend=False)
        st.plotly_chart(fig_installments, use_container_width=True)
    
    with col2:
        # Average payment value by installments
        avg_by_installments = installment_data.groupby('PAYMENT_INSTALLMENTS')['PAYMENT_VALUE'].mean().reset_index()
        avg_by_installments.columns = ['INSTALLMENTS', 'AVG_VALUE']
        
        fig_avg_installments = px.line(
            avg_by_installments,
            x='INSTALLMENTS',
            y='AVG_VALUE',
            title='Average Payment Value by Installments',
            labels={'INSTALLMENTS': 'Number of Installments', 'AVG_VALUE': 'Avg Value (R$)'},
            markers=True
        )
        fig_avg_installments.update_traces(line_color='#2ca02c', line_width=3)
        st.plotly_chart(fig_avg_installments, use_container_width=True)
    
    # Payment value distribution
    st.markdown("---")
    st.subheader("💵 Payment Value Distribution")
    
    # Filter outliers for better visualization
    payment_values = obt_data['PAYMENT_VALUE']
    q1, q99 = payment_values.quantile([0.01, 0.99])
    filtered_payments = obt_data[(payment_values >= q1) & (payment_values <= q99)]
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_hist = px.histogram(
            filtered_payments,
            x='PAYMENT_VALUE',
            nbins=50,
            title='Payment Value Distribution (1st-99th percentile)',
            labels={'PAYMENT_VALUE': 'Payment Value (R$)'},
            color_discrete_sequence=['#1f77b4']
        )
        fig_hist.update_layout(showlegend=False)
        st.plotly_chart(fig_hist, use_container_width=True)
    
    with col2:
        fig_box = px.box(
            filtered_payments,
            y='PAYMENT_VALUE',
            title='Payment Value Box Plot',
            labels={'PAYMENT_VALUE': 'Payment Value (R$)'},
            color_discrete_sequence=['#ff7f0e']
        )
        st.plotly_chart(fig_box, use_container_width=True)
    
    # Payment trends over time
    if 'ORDER_PURCHASE_TIMESTAMP' in obt_data.columns:
        st.markdown("---")
        st.subheader("📈 Payment Trends Over Time")
        
        obt_data['ORDER_DATE'] = obt_data['ORDER_PURCHASE_TIMESTAMP'].dt.date
        
        payment_trends = obt_data.groupby(['ORDER_DATE', 'PAYMENT_TYPE']).agg({
            'PAYMENT_VALUE': 'sum',
            'ORDER_ID': 'count'
        }).reset_index()
        payment_trends.columns = ['DATE', 'PAYMENT_TYPE', 'TOTAL_VALUE', 'TRANSACTION_COUNT']
        
        fig_trend = px.line(
            payment_trends,
            x='DATE',
            y='TOTAL_VALUE',
            color='PAYMENT_TYPE',
            title='Payment Value Trend by Payment Type',
            labels={'TOTAL_VALUE': 'Payment Value (R$)', 'DATE': 'Date'}
        )
        fig_trend.update_layout(height=450)
        st.plotly_chart(fig_trend, use_container_width=True)
    
    # Payment method statistics table
    st.markdown("---")
    st.subheader("📋 Payment Method Statistics")
    
    payment_stats = obt_data.groupby('PAYMENT_TYPE').agg({
        'ORDER_ID': 'count',
        'PAYMENT_VALUE': ['sum', 'mean', 'median', 'std'],
        'PAYMENT_INSTALLMENTS': 'mean'
    }).round(2)
    
    payment_stats.columns = ['Transaction Count', 'Total Value', 'Avg Value', 'Median Value', 'Std Dev', 'Avg Installments']
    payment_stats = payment_stats.sort_values('Total Value', ascending=False)
    
    st.dataframe(payment_stats, use_container_width=True)
    
    # Download button
    st.markdown("---")
    csv = payment_dist.to_csv(index=False)
    st.download_button(
        label="📥 Download Payment Data",
        data=csv,
        file_name="payment_analytics.csv",
        mime="text/csv"
    )
