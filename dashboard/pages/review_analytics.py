"""
Review Analytics dashboard page
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.data_loader import load_gold_obt_summary, load_order_summary


def render():
    """Render review analytics page"""
    
    st.title("⭐ Review Analytics")
    st.markdown("Customer feedback and review analysis")
    
    # Load data
    with st.spinner("Loading review data..."):
        obt_data = load_gold_obt_summary(limit=10000)
        order_summary = load_order_summary()
    
    if obt_data.empty or 'REVIEW_SCORE' not in obt_data.columns:
        st.warning("No review data available")
        return
    
    # Filter only orders with reviews
    review_data = obt_data[obt_data['REVIEW_SCORE'].notna()]
    
    if review_data.empty:
        st.warning("No reviews found in the dataset")
        return
    
    # Review KPIs
    st.subheader("📊 Review Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_reviews = len(review_data)
    avg_score = review_data['REVIEW_SCORE'].mean()
    positive_rate = (review_data['REVIEW_SCORE'] >= 4).sum() / len(review_data)
    negative_rate = (review_data['REVIEW_SCORE'] <= 2).sum() / len(review_data)
    
    col1.metric("Total Reviews", f"{total_reviews:,}")
    col2.metric("Avg Review Score", f"{avg_score:.2f} / 5.0")
    col3.metric("Positive Rate (≥4)", f"{positive_rate*100:.1f}%")
    col4.metric("Negative Rate (≤2)", f"{negative_rate*100:.1f}%", delta_color="inverse")
    
    st.markdown("---")
    
    # Review score distribution
    st.subheader("⭐ Review Score Distribution")
    
    score_dist = review_data['REVIEW_SCORE'].value_counts().sort_index().reset_index()
    score_dist.columns = ['SCORE', 'COUNT']
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        fig_bar = px.bar(
            score_dist,
            x='SCORE',
            y='COUNT',
            title='Distribution of Review Scores',
            labels={'SCORE': 'Review Score', 'COUNT': 'Number of Reviews'},
            color='SCORE',
            color_continuous_scale='RdYlGn',
            text='COUNT'
        )
        fig_bar.update_traces(texttemplate='%{text:,}', textposition='outside')
        fig_bar.update_layout(height=450, showlegend=False)
        fig_bar.update_xaxes(dtick=1)
        st.plotly_chart(fig_bar, use_container_width=True)
    
    with col2:
        fig_pie = px.pie(
            score_dist,
            values='COUNT',
            names='SCORE',
            title='Score Proportions',
            color='SCORE',
            color_discrete_sequence=px.colors.sequential.RdYlGn
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent')
        st.plotly_chart(fig_pie, use_container_width=True)
    
    # Review sentiment analysis
    if 'REVIEW_SENTIMENT' in review_data.columns:
        st.markdown("---")
        st.subheader("😊 Review Sentiment")
        
        sentiment_data = review_data['REVIEW_SENTIMENT'].value_counts().reset_index()
        sentiment_data.columns = ['SENTIMENT', 'COUNT']
        
        fig_sentiment = px.bar(
            sentiment_data,
            x='SENTIMENT',
            y='COUNT',
            title='Review Sentiment Distribution',
            labels={'SENTIMENT': 'Sentiment', 'COUNT': 'Number of Reviews'},
            color='SENTIMENT',
            color_discrete_map={
                'positive': '#2ca02c',
                'neutral': '#ff7f0e',
                'negative': '#d62728'
            }
        )
        st.plotly_chart(fig_sentiment, use_container_width=True)
    
    # Review scores by product category
    if 'PRODUCT_CATEGORY' in review_data.columns:
        st.markdown("---")
        st.subheader("📦 Review Scores by Product Category")
        
        category_reviews = review_data.groupby('PRODUCT_CATEGORY').agg({
            'REVIEW_SCORE': ['mean', 'count']
        }).reset_index()
        category_reviews.columns = ['CATEGORY', 'AVG_SCORE', 'REVIEW_COUNT']
        category_reviews = category_reviews[category_reviews['REVIEW_COUNT'] >= 10]  # Min 10 reviews
        category_reviews = category_reviews.sort_values('AVG_SCORE', ascending=False)
        
        col1, col2 = st.columns(2)
        
        with col1:
            top_categories = category_reviews.head(15)
            fig_top = px.bar(
                top_categories,
                x='AVG_SCORE',
                y='CATEGORY',
                orientation='h',
                title='Top 15 Categories by Review Score (min 10 reviews)',
                labels={'AVG_SCORE': 'Avg Score', 'CATEGORY': 'Category'},
                color='AVG_SCORE',
                color_continuous_scale='RdYlGn',
                range_color=[1, 5]
            )
            fig_top.update_layout(height=500, showlegend=False)
            st.plotly_chart(fig_top, use_container_width=True)
        
        with col2:
            bottom_categories = category_reviews.tail(15)
            fig_bottom = px.bar(
                bottom_categories,
                x='AVG_SCORE',
                y='CATEGORY',
                orientation='h',
                title='Bottom 15 Categories by Review Score (min 10 reviews)',
                labels={'AVG_SCORE': 'Avg Score', 'CATEGORY': 'Category'},
                color='AVG_SCORE',
                color_continuous_scale='RdYlGn',
                range_color=[1, 5]
            )
            fig_bottom.update_layout(height=500, showlegend=False)
            st.plotly_chart(fig_bottom, use_container_width=True)
    
    # Review score vs delivery performance
    if 'ACTUAL_DELIVERY_DAYS' in review_data.columns:
        st.markdown("---")
        st.subheader("📊 Review Score vs Delivery Performance")
        
        # Filter valid delivery data
        delivery_review_data = review_data[
            (review_data['ACTUAL_DELIVERY_DAYS'].notna()) & 
            (review_data['ACTUAL_DELIVERY_DAYS'] > 0) &
            (review_data['ACTUAL_DELIVERY_DAYS'] < 100)
        ]
        
        if not delivery_review_data.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                # Scatter plot
                fig_scatter = px.scatter(
                    delivery_review_data.sample(min(2000, len(delivery_review_data))),
                    x='ACTUAL_DELIVERY_DAYS',
                    y='REVIEW_SCORE',
                    title='Review Score vs Delivery Days (Sample)',
                    labels={'ACTUAL_DELIVERY_DAYS': 'Delivery Days', 'REVIEW_SCORE': 'Review Score'},
                    color='REVIEW_SCORE',
                    color_continuous_scale='RdYlGn',
                    opacity=0.6
                )
                st.plotly_chart(fig_scatter, use_container_width=True)
            
            with col2:
                # Average score by delivery time buckets
                delivery_review_data['DELIVERY_BUCKET'] = pd.cut(
                    delivery_review_data['ACTUAL_DELIVERY_DAYS'],
                    bins=[0, 7, 14, 21, 30, 100],
                    labels=['0-7 days', '8-14 days', '15-21 days', '22-30 days', '30+ days']
                )
                
                bucket_avg = delivery_review_data.groupby('DELIVERY_BUCKET')['REVIEW_SCORE'].mean().reset_index()
                
                fig_bucket = px.bar(
                    bucket_avg,
                    x='DELIVERY_BUCKET',
                    y='REVIEW_SCORE',
                    title='Average Review Score by Delivery Time',
                    labels={'DELIVERY_BUCKET': 'Delivery Time', 'REVIEW_SCORE': 'Avg Review Score'},
                    color='REVIEW_SCORE',
                    color_continuous_scale='RdYlGn',
                    range_color=[1, 5]
                )
                fig_bucket.update_layout(showlegend=False)
                st.plotly_chart(fig_bucket, use_container_width=True)
    
    # Review score vs payment value
    if 'PAYMENT_VALUE' in review_data.columns:
        st.markdown("---")
        st.subheader("💰 Review Score vs Payment Value")
        
        # Filter outliers
        payment_values = review_data['PAYMENT_VALUE']
        q1, q99 = payment_values.quantile([0.01, 0.99])
        filtered_data = review_data[(payment_values >= q1) & (payment_values <= q99)]
        
        # Payment value buckets
        filtered_data['PRICE_BUCKET'] = pd.cut(
            filtered_data['PAYMENT_VALUE'],
            bins=5,
            labels=['Very Low', 'Low', 'Medium', 'High', 'Very High']
        )
        
        bucket_stats = filtered_data.groupby('PRICE_BUCKET').agg({
            'REVIEW_SCORE': ['mean', 'count']
        }).reset_index()
        bucket_stats.columns = ['PRICE_BUCKET', 'AVG_SCORE', 'COUNT']
        
        fig_price = px.bar(
            bucket_stats,
            x='PRICE_BUCKET',
            y='AVG_SCORE',
            title='Average Review Score by Price Range',
            labels={'PRICE_BUCKET': 'Price Range', 'AVG_SCORE': 'Avg Review Score'},
            color='AVG_SCORE',
            color_continuous_scale='RdYlGn',
            range_color=[1, 5],
            text='COUNT'
        )
        fig_price.update_traces(texttemplate='n=%{text}', textposition='outside')
        fig_price.update_layout(showlegend=False)
        st.plotly_chart(fig_price, use_container_width=True)
    
    # Review trends over time
    if 'ORDER_PURCHASE_TIMESTAMP' in review_data.columns:
        st.markdown("---")
        st.subheader("📈 Review Score Trends Over Time")
        
        review_data['ORDER_DATE'] = review_data['ORDER_PURCHASE_TIMESTAMP'].dt.to_period('M').dt.to_timestamp()
        
        monthly_reviews = review_data.groupby('ORDER_DATE').agg({
            'REVIEW_SCORE': ['mean', 'count']
        }).reset_index()
        monthly_reviews.columns = ['DATE', 'AVG_SCORE', 'REVIEW_COUNT']
        
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(
            x=monthly_reviews['DATE'],
            y=monthly_reviews['AVG_SCORE'],
            mode='lines+markers',
            name='Avg Score',
            line=dict(color='#1f77b4', width=3),
            yaxis='y1'
        ))
        fig_trend.add_trace(go.Bar(
            x=monthly_reviews['DATE'],
            y=monthly_reviews['REVIEW_COUNT'],
            name='Review Count',
            marker_color='lightblue',
            yaxis='y2',
            opacity=0.3
        ))
        fig_trend.update_layout(
            title='Monthly Review Score Trend',
            xaxis_title='Month',
            yaxis_title='Avg Review Score',
            yaxis2=dict(title='Review Count', overlaying='y', side='right'),
            hovermode='x unified',
            height=450
        )
        st.plotly_chart(fig_trend, use_container_width=True)
    
    # Download button
    st.markdown("---")
    csv = review_data.to_csv(index=False)
    st.download_button(
        label="📥 Download Review Data",
        data=csv,
        file_name="review_analytics.csv",
        mime="text/csv"
    )

# Import pandas for data manipulation in this module
import pandas as pd
