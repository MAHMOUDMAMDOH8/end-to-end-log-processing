import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import json
import time
import sys
import os
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Add the Scripts/produser directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'Scripts', 'produser'))

# Import the LogGenerator
try:
    from logs import LogGenerator
except ImportError:
    st.error("Could not import LogGenerator. Make sure Scripts/produser/logs.py is available.")
    st.stop()


st.set_page_config(
    page_title="E-commerce Data Dashboard",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #1f77b4;
    }
    .error-card {
        background-color: #ffe6e6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #ff4444;
    }
    .success-card {
        background-color: #e6ffe6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #44ff44;
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
    .stSelectbox > div > div > select {
        background-color: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=60)  
def load_users_data():
    """Load users data from JSON file"""
    try:
        with open('Scripts/produser/users.json', 'r', encoding='utf-8') as f:
            users_data = json.load(f)
        return pd.DataFrame(users_data)
    except Exception as e:
        st.error(f"Error loading users data: {str(e)}")
        return pd.DataFrame()

@st.cache_data(ttl=60)
def load_products_data():
    """Load products data from JSON file"""
    try:
        with open('Scripts/produser/products.json', 'r', encoding='utf-8') as f:
            products_data = json.load(f)
        return pd.DataFrame(products_data)
    except Exception as e:
        st.error(f"Error loading products data: {str(e)}")
        return pd.DataFrame()

@st.cache_data(ttl=30)  
def generate_live_events(count=100):
    """Generate live events using LogGenerator"""
    try:
        generator = LogGenerator()
        events = []
        for _ in range(count):
            event = generator.generate_log()
            events.append(event)
        return pd.DataFrame(events)
    except Exception as e:
        st.error(f"Error generating events: {str(e)}")
        return pd.DataFrame()

def get_user_stats(users_df):
    """Get user statistics from DataFrame"""
    if users_df.empty:
        return {}
    
    stats = {
        'total_users': len(users_df),
        'users_by_country': users_df['country'].value_counts().reset_index(),
        'users_by_city': users_df.groupby(['country', 'city']).size().reset_index(name='count'),
        'age_demographics': users_df['age'].value_counts().sort_index().reset_index(),
        'gender_distribution': users_df['sex'].value_counts().reset_index(),
        'avg_age': users_df['age'].mean(),
        'countries_count': users_df['country'].nunique()
    }
    
    # Rename columns for consistency
    if 'users_by_country' in stats and not stats['users_by_country'].empty:
        stats['users_by_country'].columns = ['country', 'count']
    if 'age_demographics' in stats and not stats['age_demographics'].empty:
        stats['age_demographics'].columns = ['age', 'count']
    if 'gender_distribution' in stats and not stats['gender_distribution'].empty:
        stats['gender_distribution'].columns = ['gender', 'count']
    
    return stats

def get_product_stats(products_df):
    """Get product statistics from DataFrame"""
    if products_df.empty:
        return {}
    
    stats = {
        'total_products': len(products_df),
        'category_breakdown': products_df.groupby('category').agg({
            'product_id': 'count',
            'price': 'mean'
        }).round(2).reset_index(),
        'subcategory_breakdown': products_df['subcategory'].value_counts().reset_index(),
        'brand_breakdown': products_df['brand'].value_counts().head(10).reset_index(),
        'high_value_products': products_df[products_df['price'] > 1000].head(10),
        'avg_price': products_df['price'].mean(),
        'price_distribution': products_df['price'].describe(),
        'top_rated_products': products_df.nlargest(10, 'rating')[['name', 'category', 'rating', 'price']]
    }
    
    # Rename columns for consistency
    if 'category_breakdown' in stats and not stats['category_breakdown'].empty:
        stats['category_breakdown'].columns = ['category', 'count', 'avg_price']
    if 'subcategory_breakdown' in stats and not stats['subcategory_breakdown'].empty:
        stats['subcategory_breakdown'].columns = ['subcategory', 'count']
    if 'brand_breakdown' in stats and not stats['brand_breakdown'].empty:
        stats['brand_breakdown'].columns = ['brand', 'count']
    
    return stats

def get_event_stats(events_df):
    """Get event statistics from generated events DataFrame"""
    if events_df.empty:
        return {}
    
    # Flatten geo_location for easier analysis
    if 'geo_location' in events_df.columns:
        geo_df = pd.json_normalize(events_df['geo_location'])
        events_df = pd.concat([events_df.drop('geo_location', axis=1), geo_df], axis=1)
    
    # Flatten details for easier analysis
    if 'details' in events_df.columns:
        details_df = pd.json_normalize(events_df['details'])
        events_df = pd.concat([events_df.drop('details', axis=1), details_df], axis=1)
    
    stats = {
        'total_events': len(events_df),
        'event_types': events_df['event_type'].value_counts().reset_index(),
        'error_events': len(events_df[events_df['level'] == 'ERROR']),
        'purchase_events': len(events_df[events_df['event_type'] == 'purchase']),
        'search_events': len(events_df[events_df['event_type'] == 'search']),
        'device_distribution': events_df['device_type'].value_counts().reset_index(),
        'country_distribution': events_df['country'].value_counts().reset_index() if 'country' in events_df.columns else pd.DataFrame(),
        'recent_events': events_df.head(20),
        'revenue_data': events_df[events_df['event_type'] == 'purchase']['amount'].sum() if 'amount' in events_df.columns else 0,
        'avg_session_duration': events_df['session_duration'].mean(),
        'geographic_events': events_df.groupby(['country', 'city']).size().reset_index(name='count') if all(col in events_df.columns for col in ['country', 'city']) else pd.DataFrame()
    }
    
    # Rename columns for consistency
    if 'event_types' in stats and not stats['event_types'].empty:
        stats['event_types'].columns = ['event_type', 'count']
    if 'device_distribution' in stats and not stats['device_distribution'].empty:
        stats['device_distribution'].columns = ['device_type', 'count']
    if 'country_distribution' in stats and not stats['country_distribution'].empty:
        stats['country_distribution'].columns = ['country', 'count']
    
    return stats

def get_geographic_data(events_df):
    """Get geographic data for world map from events"""
    if events_df.empty:
        return pd.DataFrame()
    
    # Flatten geo_location if it exists
    if 'geo_location' in events_df.columns:
        geo_df = pd.json_normalize(events_df['geo_location'])
        events_df = pd.concat([events_df.drop('geo_location', axis=1), geo_df], axis=1)
    
    if 'country' not in events_df.columns:
        return pd.DataFrame()
    
    # Define coordinates for countries
    coordinates = {
        'EG': {'lat': 30.0444, 'lon': 31.2357, 'name': 'Egypt'},
        'US': {'lat': 40.7128, 'lon': -74.0060, 'name': 'USA'},
        'UK': {'lat': 51.5074, 'lon': -0.1278, 'name': 'United Kingdom'},
        'DE': {'lat': 52.5200, 'lon': 13.4050, 'name': 'Germany'},
        'IN': {'lat': 28.6139, 'lon': 77.2090, 'name': 'India'},
        'FR': {'lat': 48.8566, 'lon': 2.3522, 'name': 'France'},
        'ES': {'lat': 40.4168, 'lon': -3.7038, 'name': 'Spain'},
        'SA': {'lat': 24.7136, 'lon': 46.6753, 'name': 'Saudi Arabia'}
    }
    
    country_counts = events_df['country'].value_counts()
    
    geo_data = []
    for country_code, count in country_counts.items():
        if country_code in coordinates:
            coords = coordinates[country_code]
            geo_data.append({
                'country': coords['name'],
                'country_code': country_code,
                'latitude': coords['lat'],
                'longitude': coords['lon'],
                'events': count
            })
    
    return pd.DataFrame(geo_data)

def create_world_map(geo_df):
    """Create interactive world map"""
    if geo_df.empty:
        return go.Figure()
    
    # Create the scatter geo plot
    fig = go.Figure(data=go.Scattergeo(
        lon=geo_df['longitude'],
        lat=geo_df['latitude'],
        text=geo_df['country'] + '<br>' + geo_df['events'].astype(str) + ' events',
        mode='markers+text',
        marker=dict(
            size=np.sqrt(geo_df['events']) * 5,  # Scale marker size by events
            color=geo_df['events'],
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Events Count"),
            sizemode='diameter',
            sizemin=10,
            line=dict(width=2, color='white')
        ),
        textposition='top center',
        hovertemplate='<b>%{text}</b><br>Coordinates: %{lat}, %{lon}<extra></extra>'
    ))
    
    fig.update_layout(
        title="Global E-commerce Activity Distribution",
        geo=dict(
            projection_type='natural earth',
            showland=True,
            landcolor='rgb(243, 243, 243)',
            coastlinecolor='rgb(204, 204, 204)',
            showocean=True,
            oceancolor='rgb(230, 245, 255)',
            showlakes=True,
            lakecolor='rgb(230, 245, 255)',
            showrivers=True,
            rivercolor='rgb(230, 245, 255)',
            showcountries=True,
            countrycolor='rgb(204, 204, 204)'
        ),
        height=600,
        margin=dict(l=0, r=0, t=50, b=0)
    )
    
    return fig

def main():
    # Header
    st.markdown('<h1 class="main-header">E-commerce JSON Data Dashboard</h1>', unsafe_allow_html=True)
    
    # Load data
    with st.spinner("Loading data..."):
        users_df = load_users_data()
        products_df = load_products_data()
        events_df = generate_live_events(100)  # Generate 100 sample events
    
    # Sidebar for controls only
    st.sidebar.header("Dashboard Controls")
    auto_refresh = st.sidebar.checkbox("Auto-refresh Events (30s)", value=True)
    event_count = st.sidebar.slider("Number of Events to Generate", 50, 500, 100)
    refresh_button = st.sidebar.button("Refresh All Data")
    
    if refresh_button:
        st.cache_data.clear()
        st.rerun()
    
    # Show data status in sidebar
    st.sidebar.header("Data Status")
    st.sidebar.metric("Users Loaded", f"{len(users_df):,}")
    st.sidebar.metric("Products Loaded", f"{len(products_df):,}")
    st.sidebar.metric("Events Generated", f"{len(events_df):,}")
    
    # Auto-refresh logic
    if auto_refresh:
        time.sleep(1)  # Small delay for UI responsiveness
        events_df = generate_live_events(event_count)
    
    # Main navigation using tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Overview", 
        "User Analytics", 
        "Product Analytics", 
        "Event Monitoring", 
        "Geographic Analysis", 
        "Real-time Events"
    ])
    
    with tab1:
        show_overview(users_df, products_df, events_df)
    
    with tab2:
        show_user_analytics(users_df)
    
    with tab3:
        show_product_analytics(products_df)
    
    with tab4:
        show_event_monitoring(events_df)
    
    with tab5:
        show_geographic_analysis(events_df)
    
    with tab6:
        show_realtime_events(events_df)

def show_overview(users_df, products_df, events_df):
    """Show overview dashboard with key metrics"""
    st.header("System Overview")
    
    # Get stats
    user_stats = get_user_stats(users_df)
    product_stats = get_product_stats(products_df)
    event_stats = get_event_stats(events_df)
    
    # Top metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Users", f"{user_stats.get('total_users', 0):,}")
    
    with col2:
        st.metric("Total Products", f"{product_stats.get('total_products', 0):,}")
    
    with col3:
        st.metric("Generated Events", f"{event_stats.get('total_events', 0):,}")
    
    with col4:
        error_count = event_stats.get('error_events', 0)
        st.metric("Error Events", f"{error_count:,}", 
                 delta=f"{error_count} errors" if error_count > 0 else "No errors")
    
    # Charts row
    col1, col2 = st.columns(2)
    
    with col1:
        # Event types pie chart
        if 'event_types' in event_stats and not event_stats['event_types'].empty:
            fig = px.pie(
                event_stats['event_types'], 
                values='count', 
                names='event_type',
                title="Event Types Distribution",
                hole=0.4
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Product categories bar chart
        if 'category_breakdown' in product_stats and not product_stats['category_breakdown'].empty:
            fig = px.bar(
                product_stats['category_breakdown'],
                x='category',
                y='count',
                title="Products by Category",
                color='avg_price',
                color_continuous_scale='viridis'
            )
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
    
    # Additional overview metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if 'countries_count' in user_stats:
            st.metric("Countries", f"{user_stats['countries_count']}")
        if 'avg_age' in user_stats:
            st.metric("Avg User Age", f"{user_stats['avg_age']:.1f} years")
    
    with col2:
        if 'avg_price' in product_stats:
            st.metric("Avg Product Price", f"${product_stats['avg_price']:.2f}")
        if 'revenue_data' in event_stats:
            st.metric("Generated Revenue", f"${event_stats['revenue_data']:.2f}")
    
    with col3:
        if 'avg_session_duration' in event_stats:
            st.metric("Avg Session", f"{event_stats['avg_session_duration']:.0f}s")

def show_user_analytics(users_df):
    """Show detailed user analytics"""
    st.header("User Analytics")
    
    user_stats = get_user_stats(users_df)
    
    if not users_df.empty:
        # User metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Users", f"{user_stats['total_users']:,}")
        
        with col2:
            if not user_stats['users_by_country'].empty:
                top_country = user_stats['users_by_country'].iloc[0]
                st.metric("Top Country", f"{top_country['country']}", f"{top_country['count']} users")
        
        with col3:
            st.metric("Average Age", f"{user_stats['avg_age']:.1f} years")
        
        with col4:
            st.metric("Countries", f"{user_stats['countries_count']}")
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            if not user_stats['users_by_country'].empty:
                fig = px.bar(
                    user_stats['users_by_country'].head(10),
                    x='country',
                    y='count',
                    title="Users by Country (Top 10)",
                    color='count',
                    color_continuous_scale='blues'
                )
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if not user_stats['gender_distribution'].empty:
                fig = px.pie(
                    user_stats['gender_distribution'],
                    values='count',
                    names='gender',
                    title="Gender Distribution",
                    hole=0.4
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Age demographics
        if not user_stats['age_demographics'].empty:
            fig = px.histogram(
                users_df,
                x='age',
                title="Age Demographics Distribution",
                nbins=30,
                color_discrete_sequence=['lightblue']
            )
            fig.update_layout(bargap=0.1)
            st.plotly_chart(fig, use_container_width=True)
        
        # Cities table
        if not user_stats['users_by_city'].empty:
            st.subheader("Users by City")
            city_data = user_stats['users_by_city'].sort_values('count', ascending=False).head(20)
            st.dataframe(city_data, use_container_width=True)
    else:
        st.warning("No user data available. Make sure Scripts/produser/users.json exists.")

def show_product_analytics(products_df):
    """Show detailed product analytics"""
    st.header("Product Analytics")
    
    product_stats = get_product_stats(products_df)
    
    if not products_df.empty:
        # Product metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Products", f"{product_stats['total_products']:,}")
        
        with col2:
            st.metric("Avg Price", f"${product_stats['avg_price']:.2f}")
        
        with col3:
            categories = len(product_stats['category_breakdown'])
            st.metric("Categories", f"{categories}")
        
        with col4:
            if not product_stats['brand_breakdown'].empty:
                top_brand = product_stats['brand_breakdown'].iloc[0]
                st.metric("Top Brand", f"{top_brand['brand']}", f"{top_brand['count']} products")
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            if not product_stats['category_breakdown'].empty:
                fig = px.pie(
                    product_stats['category_breakdown'],
                    values='count',
                    names='category',
                    title="Product Distribution by Category",
                    hole=0.4
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if not product_stats['category_breakdown'].empty:
                fig = px.bar(
                    product_stats['category_breakdown'],
                    x='category',
                    y='avg_price',
                    title="Average Price by Category",
                    color='avg_price',
                    color_continuous_scale='RdYlGn_r'
                )
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
        
        # Price distribution
        fig = px.histogram(
            products_df,
            x='price',
            title="Product Price Distribution",
            nbins=50,
            color_discrete_sequence=['lightgreen']
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # High-value products
        if not product_stats['high_value_products'].empty:
            st.subheader("High-Value Products (>$1000)")
            high_value_display = product_stats['high_value_products'][['name', 'category', 'price', 'brand', 'rating']].copy()
            high_value_display['price'] = high_value_display['price'].apply(lambda x: f"${x:,.2f}")
            st.dataframe(high_value_display, use_container_width=True)
        
        # Top rated products
        if not product_stats['top_rated_products'].empty:
            st.subheader("Top Rated Products")
            top_rated_display = product_stats['top_rated_products'].copy()
            top_rated_display['price'] = top_rated_display['price'].apply(lambda x: f"${x:,.2f}")
            st.dataframe(top_rated_display, use_container_width=True)
    else:
        st.warning("No product data available. Make sure Scripts/produser/products.json exists.")

def show_event_monitoring(events_df):
    """Show event monitoring dashboard"""
    st.header("Event Monitoring")
    
    event_stats = get_event_stats(events_df)
    
    if not events_df.empty:
        # Event metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Events", f"{event_stats['total_events']:,}")
        
        with col2:
            st.metric("Purchases", f"{event_stats['purchase_events']:,}")
        
        with col3:
            st.metric("Searches", f"{event_stats['search_events']:,}")
        
        with col4:
            error_count = event_stats['error_events']
            st.metric("Errors", f"{error_count:,}", 
                     delta=f"Alert!" if error_count > 5 else "Normal", 
                     delta_color="inverse" if error_count > 5 else "normal")
        
        # Event analytics
        col1, col2 = st.columns(2)
        
        with col1:
            if not event_stats['event_types'].empty:
                fig = px.pie(
                    event_stats['event_types'],
                    values='count',
                    names='event_type',
                    title="Event Types Distribution",
                    hole=0.4
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if not event_stats['device_distribution'].empty:
                fig = px.bar(
                    event_stats['device_distribution'],
                    x='device_type',
                    y='count',
                    title="Device Type Distribution",
                    color='count',
                    color_continuous_scale='viridis'
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Session duration analysis
        if 'session_duration' in events_df.columns:
            fig = px.histogram(
                events_df,
                x='session_duration',
                title="Session Duration Distribution",
                nbins=30,
                color_discrete_sequence=['orange']
            )
            fig.update_layout(xaxis_title="Session Duration (seconds)")
            st.plotly_chart(fig, use_container_width=True)
        
        # Revenue metrics
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Generated Revenue", f"${event_stats['revenue_data']:.2f}")
        with col2:
            st.metric("Avg Session Duration", f"{event_stats['avg_session_duration']:.0f} seconds")
    else:
        st.warning("No event data generated. Try refreshing the page.")

def show_geographic_analysis(events_df):
    """Show geographic analysis with world map"""
    st.header("Geographic Analysis")
    
    # Get geographic data
    geo_data = get_geographic_data(events_df)
    event_stats = get_event_stats(events_df)
    
    if not geo_data.empty:
        # World map
        fig = create_world_map(geo_data)
        st.plotly_chart(fig, use_container_width=True)
        
        # Geographic metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            egypt_events = geo_data[geo_data['country_code'] == 'EG']['events'].sum() if not geo_data.empty else 0
            st.metric("Egypt Events", f"{egypt_events:,}")
        
        with col2:
            total_events = geo_data['events'].sum() if not geo_data.empty else 0
            st.metric("Total Global Events", f"{total_events:,}")
        
        with col3:
            international = total_events - egypt_events
            st.metric("International Events", f"{international:,}")
        
        # Country breakdown
        if not event_stats['country_distribution'].empty:
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.bar(
                    event_stats['country_distribution'],
                    x='country',
                    y='count',
                    title="Events by Country",
                    color='count',
                    color_continuous_scale='viridis'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = px.pie(
                    event_stats['country_distribution'],
                    values='count',
                    names='country',
                    title="Geographic Distribution",
                    hole=0.4
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Geographic breakdown table
        if not event_stats['geographic_events'].empty:
            st.subheader("Events by Location")
            geo_table = event_stats['geographic_events'].sort_values('count', ascending=False)
            st.dataframe(geo_table, use_container_width=True)
    else:
        st.warning("No geographic data available in generated events.")

def show_realtime_events(events_df):
    """Show real-time event stream"""
    st.header("Real-time Event Stream")
    
    # Controls
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Generate New Events"):
            st.cache_data.clear()
            st.rerun()
    with col2:
        st.metric("Events Generated", f"{len(events_df):,}")
    with col3:
        current_time = datetime.now().strftime("%H:%M:%S")
        st.metric("Last Updated", current_time)
    
    if not events_df.empty:
        # Recent events table
        st.subheader("Latest Events")
        
        # Format the events for display
        display_events = events_df.head(20).copy()
        
        # Select relevant columns for display
        columns_to_show = ['timestamp', 'event_type', 'user_id', 'product_id', 'level', 'device_type']
        
        # Add geo info if available
        if 'country' in events_df.columns:
            columns_to_show.append('country')
        if 'city' in events_df.columns:
            columns_to_show.append('city')
        
        # Add amount if available
        if 'amount' in events_df.columns:
            columns_to_show.append('amount')
        
        # Filter to existing columns
        existing_columns = [col for col in columns_to_show if col in display_events.columns]
        display_events = display_events[existing_columns]
        
        # Format timestamp
        if 'timestamp' in display_events.columns:
            display_events['timestamp'] = pd.to_datetime(display_events['timestamp']).dt.strftime('%H:%M:%S')
        
        # Style the dataframe
        st.dataframe(
            display_events,
            use_container_width=True,
            column_config={
                "amount": st.column_config.NumberColumn(
                    "Amount ($)",
                    format="$%.2f"
                ) if 'amount' in display_events.columns else None
            }
        )
        
        # Event timeline
        if len(events_df) > 1:
            # Create hourly event counts for timeline
            events_df['hour'] = pd.to_datetime(events_df['timestamp']).dt.hour
            hourly_events = events_df.groupby(['hour', 'event_type']).size().reset_index(name='count')
            
            fig = px.line(
                hourly_events,
                x='hour',
                y='count',
                color='event_type',
                title="Event Activity Timeline",
                markers=True
            )
            fig.update_layout(xaxis_title="Hour of Day", yaxis_title="Event Count")
            st.plotly_chart(fig, use_container_width=True)
        
        # Real-time metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            purchase_rate = len(events_df[events_df['event_type'] == 'purchase']) / len(events_df) * 100
            st.metric("Purchase Rate", f"{purchase_rate:.1f}%")
        
        with col2:
            error_rate = len(events_df[events_df['level'] == 'ERROR']) / len(events_df) * 100
            st.metric("Error Rate", f"{error_rate:.1f}%", 
                     delta="High" if error_rate > 15 else "Normal",
                     delta_color="inverse" if error_rate > 15 else "normal")
        
        with col3:
            unique_users = events_df['user_id'].nunique()
            st.metric("Active Users", f"{unique_users:,}")
    else:
        st.warning("No events generated. Try refreshing the page.")

if __name__ == "__main__":
    main() 