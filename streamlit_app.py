import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from analyze import PrizePicskAnalyzer
import plotly.express as px
import asyncio
from datetime import datetime

# Set page config
st.set_page_config(
    page_title="PrizePicks Analyzer",
    page_icon="🎯",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #dee2e6;
    }
    .confidence-high {
        color: #28a745;
    }
    .confidence-medium {
        color: #ffc107;
    }
    .confidence-low {
        color: #dc3545;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.title("🎯 PrizePicks Analyzer")
st.markdown("---")

# Sidebar for inputs
with st.sidebar:
    st.header("Analysis Parameters")
    
    sport = st.selectbox(
        "Select Sport",
        ["basketball", "football"],
        index=0
    )
    
    player_name = st.text_input(
        "Player Name",
        placeholder="Enter player name (e.g., LeBron James)"
    )
    
    betting_line = st.number_input(
        "Betting Line",
        min_value=0.0,
        max_value=200.0,
        value=25.0,
        step=0.5
    )
    
    analyze_button = st.button("Analyze Player")

# Main content
if analyze_button and player_name:
    with st.spinner('Fetching real-time data and analyzing player performance...'):
        analyzer = PrizePicskAnalyzer(sport)
        result = analyzer.analyze_player(player_name, betting_line)
        
        if result['success']:
            # Create three columns for metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    label="Average Performance",
                    value=f"{result['avg_performance']:.2f}",
                    delta=f"{result['performance_diff']:.2f} vs Line"
                )
            
            with col2:
                confidence = result['confidence_score']
                confidence_color = (
                    'confidence-high' if confidence >= 70
                    else 'confidence-medium' if confidence >= 40
                    else 'confidence-low'
                )
                st.markdown(f"""
                    <div class="metric-card">
                        <h3>Confidence Score</h3>
                        <p class="{confidence_color}" style="font-size: 24px; font-weight: bold;">
                            {confidence:.1f}%
                        </p>
                    </div>
                """, unsafe_allow_html=True)
            
            with col3:
                recommendation_color = "green" if result['recommendation'] == "Over" else "red"
                st.markdown(f"""
                    <div class="metric-card">
                        <h3>Recommendation</h3>
                        <p style="color: {recommendation_color}; font-size: 24px; font-weight: bold;">
                            {result['recommendation']}
                        </p>
                    </div>
                """, unsafe_allow_html=True)
            
            # Injury and Matchup Information
            st.markdown("---")
            st.subheader("Game Context")
            
            context_col1, context_col2 = st.columns(2)
            
            with context_col1:
                st.markdown("### 🏥 Injury Status")
                injury = result['injury_status']
                st.markdown(f"""
                    - **Status:** {injury['status']}
                    - **Details:** {injury['details']}
                    - **Last Updated:** {injury['last_updated']}
                """)
            
            with context_col2:
                st.markdown("### 🏟️ Matchup Analysis")
                matchup = result['matchup_analysis']
                st.markdown(f"""
                    - **Opponent:** {matchup['opponent']}
                    - **Opponent Rank:** {matchup['opponent_rank']}
                    - **Location:** {matchup['home_away']}
                    - **Rest Days:** {matchup['rest_days']}
                """)
            
            # Performance History
            st.markdown("---")
            st.subheader("Recent Performance")
            
            # Create performance history dataframe
            recent_games = result['recent_games']
            if recent_games:
                df = pd.DataFrame(recent_games)
                
                # Create line chart
                fig = px.line(df, x=range(len(df)), y='points', 
                             title='Recent Game Performance')
                fig.add_hline(y=betting_line, line_dash="dash", 
                             line_color="red", annotation_text="Betting Line")
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Show detailed game log
                st.markdown("### Detailed Game Log")
                st.dataframe(df)
            
            # Data freshness indicator
            st.markdown("---")
            st.markdown(f"*Data last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
            
        else:
            st.error(f"Error: {result.get('error', 'Could not analyze player')}")
else:
    # Show welcome message when no analysis is running
    st.info("👈 Enter player details in the sidebar to start analysis")
    
    # Show some tips or information
    with st.expander("How to use this analyzer"):
        st.markdown("""
            1. Select the sport (Basketball or Football)
            2. Enter the player's name exactly as it appears on PrizePicks
            3. Input the betting line from PrizePicks
            4. Click 'Analyze Player' to see detailed analysis
            
            The analyzer will provide:
            - Real-time performance metrics
            - Confidence score based on recent performance
            - Injury status and matchup analysis
            - Detailed game logs and trends
            - Betting recommendations
        """)

# Footer
st.markdown("---")
st.markdown("Made with ❤️ by Cascade")
