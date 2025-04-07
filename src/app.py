import streamlit as st
import plotly.graph_objects as go
from data_processor import DataProcessor
import pandas as pd
from typing import List, Dict, Any

def create_price_chart(df: pd.DataFrame, coin_name: str):
    """Create an interactive price chart with moving average"""
    fig = go.Figure()
    
    # Add price line
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['price'],
        name=f'{coin_name} Price',
        line=dict(color='blue')
    ))
    
    # Add moving average line
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['moving_average'],
        name='5-Day Moving Average',
        line=dict(color='red', dash='dash')
    ))
    
    fig.update_layout(
        title=f'{coin_name} Price and 5-Day Moving Average (Q1 2025)',
        xaxis_title='Date',
        yaxis_title='Price (USD)',
        hovermode='x unified'
    )
    
    return fig

def create_comparison_chart(all_data: pd.DataFrame, selected_coins: List[str]):
    """Create a comparison chart for multiple coins"""
    fig = go.Figure()
    
    # Add a line for each selected coin
    for coin_id in selected_coins:
        coin_data = all_data[all_data['coin_id'] == coin_id]
        fig.add_trace(go.Scatter(
            x=coin_data['date'],
            y=coin_data['price'],
            name=coin_id.capitalize(),
            mode='lines'
        ))
    
    fig.update_layout(
        title='Price Comparison (Q1 2025)',
        xaxis_title='Date',
        yaxis_title='Price (USD)',
        hovermode='x unified'
    )
    
    return fig

def display_coin_metrics(stats: Dict[str, Any], coin_name: str):
    """Display metrics for a single coin"""
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Mean Price", f"${stats['mean_price']:,.2f}")
    with col2:
        st.metric("Standard Deviation", f"${stats['std_price']:,.2f}")
    with col3:
        st.metric("Min Price", f"${stats['min_price']:,.2f}")
    with col4:
        st.metric("Max Price", f"${stats['max_price']:,.2f}")
    with col5:
        st.metric("Price Change", f"{stats['price_change_pct']:.2f}%")

def display_comparison_metrics(comparison: Dict[str, Any]):
    """Display comparison metrics for multiple coins"""
    st.subheader("Price Performance Comparison")
    
    # Create a DataFrame for the comparison data
    comparison_df = pd.DataFrame.from_dict(comparison, orient='index')
    comparison_df.index = comparison_df.index.str.capitalize()
    
    # Display the comparison table
    st.dataframe(comparison_df)
    
    # Add insights
    best_performer = comparison_df['price_change_pct'].idxmax()
    worst_performer = comparison_df['price_change_pct'].idxmin()
    st.info(f"Best performing coin: {best_performer} ({comparison_df.loc[best_performer, 'price_change_pct']:.2f}%)")
    st.warning(f"Worst performing coin: {worst_performer} ({comparison_df.loc[worst_performer, 'price_change_pct']:.2f}%)")

def main():
    st.set_page_config(page_title="Cryptocurrency Price Analysis", layout="wide")
    st.title("Cryptocurrency Price Analysis - Q1 2025")
    
    try:
        # Initialize data processor
        processor = DataProcessor()
        
        # Get all available coins
        all_data = processor.get_all_coins_data()
        available_coins = sorted(all_data['coin_id'].unique())
        
        # Sidebar for coin selection
        st.sidebar.header("Select Coins")
        selected_coins = st.sidebar.multiselect(
            "Choose coins to analyze",
            options=available_coins,
            format_func=lambda x: x.capitalize()
        )
        
        if not selected_coins:
            st.warning("Please select at least one coin to analyze")
            return
            
        # Show comparison features only if multiple coins are selected
        if len(selected_coins) > 1:
            # Display comparison chart
            st.subheader("Price Comparison")
            st.plotly_chart(create_comparison_chart(all_data, selected_coins), use_container_width=True)
            
            # Get and display comparison metrics
            comparison = processor.get_coin_comparison(selected_coins)
            display_comparison_metrics(comparison)
        
        # Individual coin analysis
        st.subheader("Individual Coin Analysis")
        for coin_id in selected_coins:
            st.markdown(f"### {coin_id.capitalize()}")
            
            # Get price analysis for the coin
            df, stats = processor.get_price_analysis(coin_id)
            
            # Display metrics
            display_coin_metrics(stats, coin_id.capitalize())
            
            # Display price chart
            st.plotly_chart(create_price_chart(df, coin_id.capitalize()), use_container_width=True)
            
            # Display raw data
            with st.expander("Show Raw Data"):
                st.dataframe(df)
            
            # Analysis insights
            if stats['price_change_pct'] > 0:
                st.success(f"{coin_id.capitalize()} showed a positive trend with a {stats['price_change_pct']:.2f}% increase in price.")
            else:
                st.error(f"{coin_id.capitalize()} showed a negative trend with a {stats['price_change_pct']:.2f}% decrease in price.")
            
            volatility_level = 'high' if stats['std_price'] > stats['mean_price'] * 0.1 else 'moderate'
            st.info(f"The price volatility (standard deviation) was ${stats['std_price']:,.2f}, indicating {volatility_level} market volatility.")
            
            st.markdown("---")
        
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.error("Please ensure the data collection process has been completed successfully.")

if __name__ == "__main__":
    main() 