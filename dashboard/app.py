"""
E-Commerce Analytics Dashboard
Main Streamlit application
"""
import streamlit as st
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(
    page_title="E-Commerce Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Snowflake inspired theme
st.markdown("""
<style>
    .main-header {
        font-size: 2.8rem;
        font-weight: 700;
        color: #29B5E8;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .metric-card {
        background: linear-gradient(135deg, #F0F8FF 0%, #FFFFFF 100%);
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #29B5E8;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(41, 181, 232, 0.2);
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #F0F8FF 0%, #FFFFFF 100%);
    }
    .stButton>button {
        background-color: #29B5E8;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 0.5rem 2rem;
        font-weight: 600;
        transition: background-color 0.3s;
    }
    .stButton>button:hover {
        background-color: #1E90E0;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
        color: #262730;
        font-weight: 700;
    }
    div[data-testid="stMetricLabel"] {
        color: #4A5568;
        font-weight: 600;
    }
    .streamlit-expanderHeader {
        background-color: #F0F8FF;
        border-radius: 5px;
    }
    h1, h2, h3 {
        color: #262730;
    }
    .stAlert {
        background-color: #F0F8FF;
        border-left: 5px solid #29B5E8;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<h1 class="main-header">📊 E-Commerce Analytics Dashboard</h1>', unsafe_allow_html=True)
st.markdown("---")

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/000000/business-report.png", width=80)
    st.title("Navigation")
    
    page = st.radio(
        "Select View",
        [
            "🏠 Overview",
            "📈 Sales Analytics", 
            "👥 Customer Analytics",
            "📦 Product Analytics",
            "🚚 Delivery Performance",
            "💰 Payment Analytics",
            "⭐ Review Analytics"
        ]
    )
    
    st.markdown("---")
    st.subheader("Filters")
    
    # Date range filter - Brazilian E-Commerce data is from 2016-2018
    date_range = st.date_input(
        "Date Range",
        value=(datetime(2016, 1, 1), datetime(2018, 12, 31)),
        min_value=datetime(2016, 1, 1),
        max_value=datetime(2018, 12, 31)
    )
    
    # Additional filters
    st.selectbox("Order Status", ["All", "delivered", "shipped", "canceled"])
    st.selectbox("Region", ["All", "North", "South", "East", "West"])
    
    st.markdown("---")
    st.info("🔄 Data from: 2016-2018 | Brazilian E-Commerce Dataset")

# Main content area
if page == "🏠 Overview":
    from pages import overview
    overview.render()
    
elif page == "📈 Sales Analytics":
    from pages import sales_analytics
    sales_analytics.render()
    
elif page == "👥 Customer Analytics":
    from pages import customer_analytics
    customer_analytics.render()
    
elif page == "📦 Product Analytics":
    from pages import product_analytics
    product_analytics.render()
    
elif page == "🚚 Delivery Performance":
    from pages import delivery_performance
    delivery_performance.render()
    
elif page == "💰 Payment Analytics":
    from pages import payment_analytics
    payment_analytics.render()
    
elif page == "⭐ Review Analytics":
    from pages import review_analytics
    review_analytics.render()

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <p>Powered by dbt + Snowflake + Streamlit | Data Engineering Project | Created by HAKKACHE</p>
    </div>
    """,
    unsafe_allow_html=True
)
