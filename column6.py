import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from pathlib import Path
import numpy as np

def render_column6(method, site):
    """Render prediction visualization for Column 6 - Pre2"""
    
    st.markdown('<h3>📈 Best Curve Fitting - Regression Method</h3>', unsafe_allow_html=True)
    
    # Load prediction data
    csv_path = Path(f"data/Prediction/{method}/{site}")
    prediction_path = csv_path / "transect_timeseries_predicted.csv"
    stats_path = csv_path / "coastal_change_statistics_predicted.csv"
    
    if not prediction_path.exists():
        st.warning(f"""
        ⚠️ **Prediction data not found!**
        
        Please ensure the following file exists:
        - {prediction_path}
        
        Expected CSV structure:
        - dates: Date column
        - year: Year column
        - NA1_distance_m, NA2_distance_m, ...: Distance columns for each transect
        """)
        return
    
    try:
        # Load data
        prediction_data = pd.read_csv(prediction_path)
        
        # Convert dates to datetime if needed
        if 'dates' in prediction_data.columns:
            prediction_data['dates'] = pd.to_datetime(prediction_data['dates'])
        
        # Get list of transects
        transects = [col for col in prediction_data.columns if col.endswith('_distance_m')]
        transect_names = [col.replace('_distance_m', '') for col in transects]
        
        # Selectbox to choose transect
        selected_transect_col = st.selectbox(
            "**Select Transect:**",
            transects,
            format_func=lambda x: x.replace('_distance_m', ''),
            key="prediction_pre2_transect_selector"
        )
        
        selected_transect_name = selected_transect_col.replace('_distance_m', '')
        
        # Filter data for selected transect (remove NaN values)
        transect_data = prediction_data[['year', selected_transect_col]].dropna()
        
        # Load statistics if available
        stats_available = False
        if stats_path.exists():
            stats_data = pd.read_csv(stats_path)
            stats_row = stats_data[stats_data['Transect'] == selected_transect_name]
            if not stats_row.empty:
                stats_available = True
                stats = stats_row.iloc[0]
        
        # Create figure
        fig = go.Figure()
        
        # Add predicted data line
        fig.add_trace(go.Scatter(
            x=transect_data['year'],
            y=transect_data[selected_transect_col],
            mode='lines+markers',
            name='Predicted Position',
            line=dict(color='red', width=3),
            marker=dict(size=8),
            hovertemplate='<b>Year:</b> %{x}<br><b>Predicted:</b> %{y:.2f}m<extra></extra>'
        ))
        
        # Add zero line
        fig.add_hline(y=0, line_dash="dash", line_color="black", line_width=1)
        
        # Determine accretion/erosion zones
        accretion_mask = transect_data[selected_transect_col] > 0
        erosion_mask = transect_data[selected_transect_col] < 0
        
        # Add accretion area (green fill)
        if accretion_mask.any():
            accretion_data = transect_data[selected_transect_col].copy()
            accretion_data[~accretion_mask] = 0
            
            fig.add_trace(go.Scatter(
                x=transect_data['year'],
                y=accretion_data,
                fill='tozeroy',
                fillcolor='rgba(144, 238, 144, 0.3)',
                line=dict(width=0),
                name='Accretion Zone',
                showlegend=True,
                hoverinfo='skip'
            ))
        
        # Add erosion area (red fill)
        if erosion_mask.any():
            erosion_data = transect_data[selected_transect_col].copy()
            erosion_data[~erosion_mask] = 0
            
            fig.add_trace(go.Scatter(
                x=transect_data['year'],
                y=erosion_data,
                fill='tozeroy',
                fillcolor='rgba(255, 182, 193, 0.3)',
                line=dict(width=0),
                name='Erosion Zone',
                showlegend=True,
                hoverinfo='skip'
            ))
        
        # Update layout
        title_text = f"Shoreline Position Prediction - {selected_transect_name}"
        if stats_available:
            title_text += f" | Rate: {stats['Rate_m_per_year']:.2f}m/yr | Net: {stats['Net_Change_m']:.2f}m"
        
        fig.update_layout(
            title=title_text,
            xaxis_title="Year",
            yaxis_title="Position (m)",
            hovermode='x unified',
            height=600,
            showlegend=True,
            paper_bgcolor='#ffffff',
            plot_bgcolor='#ffffff',
            font=dict(color='#000000', size=12),
            title_font=dict(color='#000000', size=14),
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01,
                bgcolor="rgba(255, 255, 255, 0.95)",
                bordercolor="#d0d5dd",
                borderwidth=2,
                font=dict(color='#000000', size=11)
            ),
            xaxis=dict(
                showgrid=True,
                gridcolor='#e9ecef',
                gridwidth=1,
                title_font=dict(color='#000000'),
                tickfont=dict(color='#000000'),
                dtick=1  # Show every year
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='#e9ecef',
                gridwidth=1,
                zeroline=True,
                zerolinecolor='#000000',
                zerolinewidth=2,
                title_font=dict(color='#000000'),
                tickfont=dict(color='#000000')
            )
        )
        
        # Display the chart
        st.plotly_chart(fig, use_container_width=True, config={
            'displayModeBar': True,
            'displaylogo': False,
            'modeBarButtonsToRemove': ['lasso2d', 'select2d']
        })
        
        # Display prediction statistics if available
        if stats_available:
            st.markdown('<h4 style="margin-top: 1.5rem;">📊 Prediction Statistics</h4>', unsafe_allow_html=True)
            
            # Display metrics in columns
            metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
            
            with metric_col1:
                st.metric("Mean Change", f"{stats['Mean_Change_m']:.2f} m")
            
            with metric_col2:
                st.metric("Std Deviation", f"{stats['Std_Dev_m']:.2f} m")
            
            with metric_col3:
                st.metric("Net Change", f"{stats['Net_Change_m']:.2f} m")
            
            with metric_col4:
                st.metric("Rate", f"{stats['Rate_m_per_year']:.2f} m/yr")
            
            # Additional statistics
            st.markdown('<h4 style="margin-top: 1rem;">📈 Extremes</h4>', unsafe_allow_html=True)
            
            extreme_col1, extreme_col2, extreme_col3 = st.columns(3)
            
            with extreme_col1:
                st.metric("Max Erosion", f"{stats['Max_Erosion_m']:.2f} m", delta=None)
            
            with extreme_col2:
                st.metric("Max Accretion", f"{stats['Max_Accretion_m']:.2f} m", delta=None)
            
            with extreme_col3:
                st.metric("N Points", f"{int(stats['N_Points'])}")
        
        # Display trend analysis
        st.markdown('<h4 style="margin-top: 1.5rem;">📉 Trend Analysis</h4>', unsafe_allow_html=True)
        
        # Calculate trend
        if len(transect_data) > 1:
            # Linear regression
            x = transect_data['year'].values
            y = transect_data[selected_transect_col].values
            
            # Calculate slope and intercept
            n = len(x)
            slope = (n * np.sum(x * y) - np.sum(x) * np.sum(y)) / (n * np.sum(x**2) - np.sum(x)**2)
            intercept = (np.sum(y) - slope * np.sum(x)) / n
            
            # Determine trend
            if slope > 0:
                trend = "⬆️ Accretion (Positive Trend)"
                trend_color = "green"
            elif slope < 0:
                trend = "⬇️ Erosion (Negative Trend)"
                trend_color = "red"
            else:
                trend = "➡️ Stable"
                trend_color = "blue"
            
            st.markdown(f"**Trend:** <span style='color: {trend_color}; font-weight: bold;'>{trend}</span>", unsafe_allow_html=True)
            st.markdown(f"**Slope:** {slope:.4f} m/year")
            st.markdown(f"**Projected change by 2030:** {slope * (2030 - transect_data['year'].iloc[0]):.2f} m")
        
    except Exception as e:
        st.error(f"❌ Error loading prediction data: {str(e)}")
        import traceback
        with st.expander("Show detailed error"):
            st.code(traceback.format_exc())
