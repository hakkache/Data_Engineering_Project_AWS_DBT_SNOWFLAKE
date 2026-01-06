"""
Delivery Performance dashboard page
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.data_loader import get_delivery_performance_by_state, load_gold_obt_summary


def render():
    """Render delivery performance page"""
    
    st.title("🚚 Delivery Performance")
    st.markdown("Logistics and delivery metrics analysis")
    
    # Load data
    with st.spinner("Loading delivery data..."):
        state_delivery = get_delivery_performance_by_state()
        obt_data = load_gold_obt_summary(limit=10000)
    
    if state_delivery.empty:
        st.warning("No delivery data available")
        return
    
    # Overall delivery KPIs
    st.subheader("📊 Delivery Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    avg_delivery_days = state_delivery['AVG_DELIVERY_DAYS'].mean()
    overall_late_rate = state_delivery['LATE_DELIVERY_RATE'].mean()
    total_deliveries = state_delivery['ORDER_COUNT'].sum()
    best_state = state_delivery.nsmallest(1, 'AVG_DELIVERY_DAYS')['CUSTOMER_STATE'].values[0]
    
    col1.metric("Avg Delivery Days", f"{avg_delivery_days:.1f} days")
    col2.metric("Late Delivery Rate", f"{overall_late_rate*100:.1f}%", delta_color="inverse")
    col3.metric("Total Deliveries", f"{total_deliveries:,}")
    col4.metric("Best Performing State", best_state)
    
    st.markdown("---")
    
    # Delivery performance by state
    st.subheader("🗺️ Delivery Performance by State")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_delivery_days = px.bar(
            state_delivery.sort_values('AVG_DELIVERY_DAYS').head(15),
            x='AVG_DELIVERY_DAYS',
            y='CUSTOMER_STATE',
            orientation='h',
            title='Average Delivery Days (Top 15 States)',
            labels={'AVG_DELIVERY_DAYS': 'Avg Days', 'CUSTOMER_STATE': 'State'},
            color='AVG_DELIVERY_DAYS',
            color_continuous_scale='RdYlGn_r'
        )
        fig_delivery_days.update_layout(height=500, showlegend=False)
        st.plotly_chart(fig_delivery_days, use_container_width=True)
    
    with col2:
        fig_late_rate = px.bar(
            state_delivery.sort_values('LATE_DELIVERY_RATE', ascending=False).head(15),
            x='LATE_DELIVERY_RATE',
            y='CUSTOMER_STATE',
            orientation='h',
            title='Late Delivery Rate (Top 15 States)',
            labels={'LATE_DELIVERY_RATE': 'Late Rate', 'CUSTOMER_STATE': 'State'},
            color='LATE_DELIVERY_RATE',
            color_continuous_scale='Reds'
        )
        fig_late_rate.update_layout(height=500, showlegend=False)
        fig_late_rate.update_xaxes(tickformat='.0%')
        st.plotly_chart(fig_late_rate, use_container_width=True)
    
    # Delivery volume by state
    st.markdown("---")
    st.subheader("📦 Delivery Volume by State")
    
    fig_volume = px.bar(
        state_delivery.sort_values('ORDER_COUNT', ascending=False).head(20),
        x='CUSTOMER_STATE',
        y='ORDER_COUNT',
        title='Top 20 States by Delivery Volume',
        labels={'ORDER_COUNT': 'Number of Deliveries', 'CUSTOMER_STATE': 'State'},
        color='ORDER_COUNT',
        color_continuous_scale='Blues'
    )
    fig_volume.update_layout(height=450, showlegend=False)
    st.plotly_chart(fig_volume, use_container_width=True)
    
    # Delivery days distribution
    if not obt_data.empty and 'ACTUAL_DELIVERY_DAYS' in obt_data.columns:
        st.markdown("---")
        st.subheader("📊 Delivery Days Distribution")
        
        # Filter valid delivery data
        delivery_data = obt_data[
            (obt_data['ACTUAL_DELIVERY_DAYS'].notna()) & 
            (obt_data['ACTUAL_DELIVERY_DAYS'] > 0) &
            (obt_data['ACTUAL_DELIVERY_DAYS'] < 100)  # Remove outliers
        ]
        
        if not delivery_data.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                fig_hist = px.histogram(
                    delivery_data,
                    x='ACTUAL_DELIVERY_DAYS',
                    nbins=50,
                    title='Distribution of Delivery Days',
                    labels={'ACTUAL_DELIVERY_DAYS': 'Delivery Days'},
                    color_discrete_sequence=['#1f77b4']
                )
                fig_hist.update_layout(showlegend=False)
                st.plotly_chart(fig_hist, use_container_width=True)
            
            with col2:
                fig_box = px.box(
                    delivery_data,
                    y='ACTUAL_DELIVERY_DAYS',
                    title='Delivery Days Box Plot',
                    labels={'ACTUAL_DELIVERY_DAYS': 'Delivery Days'},
                    color_discrete_sequence=['#2ca02c']
                )
                st.plotly_chart(fig_box, use_container_width=True)
            
            # Late delivery analysis
            st.markdown("---")
            st.subheader("⏰ On-Time vs Late Deliveries")
            
            late_analysis = delivery_data.groupby('IS_LATE_DELIVERY').size().reset_index()
            late_analysis.columns = ['STATUS', 'COUNT']
            late_analysis['STATUS'] = late_analysis['STATUS'].map({0: 'On Time', 1: 'Late'})
            
            fig_late = px.pie(
                late_analysis,
                values='COUNT',
                names='STATUS',
                title='Delivery Status Distribution',
                color='STATUS',
                color_discrete_map={'On Time': '#2ca02c', 'Late': '#d62728'},
                hole=0.4
            )
            fig_late.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_late, use_container_width=True)
            
            # Delivery days vs estimated days
            st.markdown("---")
            st.subheader("📅 Actual vs Estimated Delivery Days")
            
            if 'ESTIMATED_DELIVERY_DAYS' in delivery_data.columns:
                comparison_data = delivery_data[
                    (delivery_data['ESTIMATED_DELIVERY_DAYS'].notna()) &
                    (delivery_data['ESTIMATED_DELIVERY_DAYS'] > 0)
                ].sample(min(1000, len(delivery_data)))
                
                fig_comparison = px.scatter(
                    comparison_data,
                    x='ESTIMATED_DELIVERY_DAYS',
                    y='ACTUAL_DELIVERY_DAYS',
                    title='Actual vs Estimated Delivery Days (Sample)',
                    labels={
                        'ESTIMATED_DELIVERY_DAYS': 'Estimated Days',
                        'ACTUAL_DELIVERY_DAYS': 'Actual Days'
                    },
                    color='IS_LATE_DELIVERY',
                    color_discrete_map={0: '#2ca02c', 1: '#d62728'},
                    opacity=0.6
                )
                # Add diagonal line (perfect estimation)
                fig_comparison.add_trace(go.Scatter(
                    x=[0, 50],
                    y=[0, 50],
                    mode='lines',
                    name='Perfect Estimation',
                    line=dict(color='gray', dash='dash')
                ))
                fig_comparison.update_layout(height=500)
                st.plotly_chart(fig_comparison, use_container_width=True)
    
    # State performance table
    st.markdown("---")
    st.subheader("📋 State Performance Summary")
    
    state_display = state_delivery.copy()
    state_display['AVG_DELIVERY_DAYS'] = state_display['AVG_DELIVERY_DAYS'].round(1)
    state_display['LATE_DELIVERY_RATE'] = (state_display['LATE_DELIVERY_RATE'] * 100).round(1)
    state_display['AVG_REVIEW_SCORE'] = state_display['AVG_REVIEW_SCORE'].round(2)
    
    st.dataframe(
        state_display,
        use_container_width=True,
        height=400
    )
    
    # Download button
    st.markdown("---")
    csv = state_delivery.to_csv(index=False)
    st.download_button(
        label="📥 Download Delivery Data",
        data=csv,
        file_name="delivery_performance.csv",
        mime="text/csv"
    )
