"""
Product Analytics dashboard page
"""
import streamlit as st
import plotly.express as px
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.data_loader import get_top_products, load_gold_obt_summary


def render():
    """Render product analytics page"""
    
    st.title("📦 Product Analytics")
    st.markdown("Product performance and category analysis")
    
    # Load data
    with st.spinner("Loading product data..."):
        products = get_top_products(limit=20)
        obt_data = load_gold_obt_summary(limit=5000)
    
    if products.empty:
        st.warning("No product data available")
        return
    
    # Product KPIs
    st.subheader("📊 Product Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_categories = len(products)
    total_revenue = products['TOTAL_REVENUE'].sum()
    avg_price = products['AVG_PRICE'].mean()
    avg_review = products['AVG_REVIEW_SCORE'].mean()
    
    col1.metric("Product Categories", f"{total_categories}")
    col2.metric("Total Revenue", f"R$ {total_revenue:,.2f}")
    col3.metric("Avg Product Price", f"R$ {avg_price:,.2f}")
    col4.metric("Avg Review Score", f"{avg_review:.2f}/5")
    
    st.markdown("---")
    
    # Top categories by revenue
    st.subheader("💰 Top Product Categories by Revenue")
    
    fig_revenue = px.bar(
        products.head(15),
        x='TOTAL_REVENUE',
        y='PRODUCT_CATEGORY',
        orientation='h',
        title='Top 15 Categories by Revenue',
        labels={'TOTAL_REVENUE': 'Revenue (R$)', 'PRODUCT_CATEGORY': 'Category'},
        color='TOTAL_REVENUE',
        color_continuous_scale='Blues',
        text='TOTAL_REVENUE'
    )
    fig_revenue.update_traces(texttemplate='R$ %{text:,.0f}', textposition='outside')
    fig_revenue.update_layout(height=600, showlegend=False)
    st.plotly_chart(fig_revenue, use_container_width=True)
    
    # Category analysis
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Categories by Order Volume")
        
        fig_orders = px.bar(
            products.head(10),
            x='ORDER_COUNT',
            y='PRODUCT_CATEGORY',
            orientation='h',
            title='Top 10 Categories by Orders',
            color='ORDER_COUNT',
            color_continuous_scale='Oranges'
        )
        fig_orders.update_layout(showlegend=False)
        st.plotly_chart(fig_orders, use_container_width=True)
    
    with col2:
        st.subheader("⭐ Categories by Review Score")
        
        fig_reviews = px.bar(
            products.sort_values('AVG_REVIEW_SCORE', ascending=False).head(10),
            x='AVG_REVIEW_SCORE',
            y='PRODUCT_CATEGORY',
            orientation='h',
            title='Top 10 Categories by Reviews',
            color='AVG_REVIEW_SCORE',
            color_continuous_scale='RdYlGn',
            range_color=[1, 5]
        )
        fig_reviews.update_layout(showlegend=False)
        st.plotly_chart(fig_reviews, use_container_width=True)
    
    # Price vs Performance scatter
    st.markdown("---")
    st.subheader("💵 Price vs Performance Analysis")
    
    fig_scatter = px.scatter(
        products,
        x='AVG_PRICE',
        y='ORDER_COUNT',
        size='TOTAL_REVENUE',
        color='AVG_REVIEW_SCORE',
        hover_data=['PRODUCT_CATEGORY'],
        title='Price vs Order Volume (bubble size = revenue)',
        labels={
            'AVG_PRICE': 'Average Price (R$)',
            'ORDER_COUNT': 'Order Count',
            'AVG_REVIEW_SCORE': 'Avg Review'
        },
        color_continuous_scale='RdYlGn',
        range_color=[1, 5]
    )
    fig_scatter.update_layout(height=500)
    st.plotly_chart(fig_scatter, use_container_width=True)
    
    # Category comparison table
    st.markdown("---")
    st.subheader("📋 Category Performance Table")
    
    # Format the dataframe
    products_display = products.copy()
    products_display['TOTAL_REVENUE'] = products_display['TOTAL_REVENUE'].apply(lambda x: f"R$ {x:,.2f}")
    products_display['AVG_PRICE'] = products_display['AVG_PRICE'].apply(lambda x: f"R$ {x:,.2f}")
    products_display['AVG_REVIEW_SCORE'] = products_display['AVG_REVIEW_SCORE'].round(2)
    
    st.dataframe(
        products_display,
        use_container_width=True,
        height=400
    )
    
    # Product trends over time (if OBT data available)
    if not obt_data.empty and 'PRODUCT_CATEGORY' in obt_data.columns:
        st.markdown("---")
        st.subheader("📅 Category Trends Over Time")
        
        # Get top 5 categories
        top_5_cats = products.head(5)['PRODUCT_CATEGORY'].tolist()
        
        # Filter OBT data
        trend_data = obt_data[obt_data['PRODUCT_CATEGORY'].isin(top_5_cats)]
        
        if not trend_data.empty:
            # Group by date and category
            trend_data['ORDER_DATE'] = trend_data['ORDER_PURCHASE_TIMESTAMP'].dt.date
            trend_summary = trend_data.groupby(['ORDER_DATE', 'PRODUCT_CATEGORY']).agg({
                'ORDER_ID': 'count',
                'PAYMENT_VALUE': 'sum'
            }).reset_index()
            trend_summary.columns = ['DATE', 'CATEGORY', 'ORDERS', 'REVENUE']
            
            fig_trend = px.line(
                trend_summary,
                x='DATE',
                y='REVENUE',
                color='CATEGORY',
                title='Revenue Trend - Top 5 Categories',
                labels={'REVENUE': 'Revenue (R$)', 'DATE': 'Date'}
            )
            fig_trend.update_layout(height=450)
            st.plotly_chart(fig_trend, use_container_width=True)
    
    # Download button
    st.markdown("---")
    csv = products.to_csv(index=False)
    st.download_button(
        label="📥 Download Product Data",
        data=csv,
        file_name="product_analytics.csv",
        mime="text/csv"
    )
