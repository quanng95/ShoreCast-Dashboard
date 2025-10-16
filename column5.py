import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.colors
import geopandas as gpd
import pandas as pd
from pathlib import Path
import numpy as np

def render_column5(method, site):
    """Render prediction visualization for Column 5 - Pre1"""
    
    st.markdown('<h3>📈 Bruun Rules Prediction (2025-2100)</h3>', unsafe_allow_html=True)
    
    base_path = Path(f"data/Prediction/{method}/{site}")
    
    # Define SLR scenarios
    slr_scenarios = {
        "0.1m Sea Level Rise": "SLR_0_1m",
        "0.2m Sea Level Rise": "SLR_0_2m",
        "0.3m Sea Level Rise": "SLR_0_3m",
        "0.5m Sea Level Rise": "SLR_0_5m",
        "1.0m Sea Level Rise": "SLR_1_0m"
    }
    
    # Dropdown to select SLR scenario
    selected_slr = st.selectbox(
        "**Select Sea Level Rise Scenario:**",
        list(slr_scenarios.keys()),
        key="prediction_slr_scenario_selector"
    )
    
    slr_folder = slr_scenarios[selected_slr]
    
    # Paths
    historical_path = base_path / slr_folder / "shorelines_2019_2024.shp"
    prediction_path = base_path / slr_folder / "shorelines_2025_2100.shp"
    
    files_exist = historical_path.exists() and prediction_path.exists()
    
    if files_exist:
        try:
            # Load shapefiles
            @st.cache_data
            def load_shapefiles(historical_path, prediction_path):
                historical = gpd.read_file(historical_path)
                prediction = gpd.read_file(prediction_path)
                
                # Remove None geometries
                historical = historical[historical.geometry.notna()]
                prediction = prediction[prediction.geometry.notna()]
                
                return historical, prediction
            
            historical, prediction = load_shapefiles(str(historical_path), str(prediction_path))
            
            # Auto-detect year field
            def find_year_field(gdf, possible_names):
                for name in possible_names:
                    if name in gdf.columns:
                        return name
                return None
            
            year_field_hist = find_year_field(historical, ['year', 'Year', 'YEAR'])
            year_field_pred = find_year_field(prediction, ['year', 'Year', 'YEAR'])
            
            if not year_field_hist or not year_field_pred:
                st.error("❌ Cannot find year field in shapefiles!")
                return
            
            # Calculate shoreline length for each year
            def calculate_shoreline_metrics(gdf, year_field):
                years = []
                lengths = []
                positions = []
                
                for year in sorted(gdf[year_field].unique()):
                    year_data = gdf[gdf[year_field] == year]
                    
                    # Calculate total length
                    total_length = year_data.geometry.length.sum()
                    
                    # Calculate mean position (centroid)
                    if not year_data.empty:
                        centroids = year_data.geometry.centroid
                        mean_lat = centroids.y.mean()
                        mean_lon = centroids.x.mean()
                        
                        years.append(year)
                        lengths.append(total_length)
                        positions.append(mean_lat)  # Using latitude as proxy for position
                
                return pd.DataFrame({
                    'year': years,
                    'length': lengths,
                    'position': positions
                })
            
            hist_metrics = calculate_shoreline_metrics(historical, year_field_hist)
            pred_metrics = calculate_shoreline_metrics(prediction, year_field_pred)
            
            # Calculate change relative to baseline (2019 or first year)
            if len(hist_metrics) > 0:
                baseline_position = hist_metrics['position'].iloc[0]
                hist_metrics['change_m'] = (hist_metrics['position'] - baseline_position) * 111000  # Convert degrees to meters
                pred_metrics['change_m'] = (pred_metrics['position'] - baseline_position) * 111000
            
            # Create subplots
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=(
                    f'Shoreline Position Change - {selected_slr}',
                    f'Shoreline Length Over Time',
                    f'Rate of Change Analysis',
                    f'Cumulative Change Projection'
                ),
                specs=[[{"type": "scatter"}, {"type": "scatter"}],
                       [{"type": "bar"}, {"type": "scatter"}]]
            )
            
            # Color mapping
            slr_colors = {
                "0.1m Sea Level Rise": "blue",
                "0.2m Sea Level Rise": "green",
                "0.3m Sea Level Rise": "gold",
                "0.5m Sea Level Rise": "orange",
                "1.0m Sea Level Rise": "red"
            }
            color = slr_colors.get(selected_slr, "purple")
            
            # Convert color name to rgba for fill
            color_map = {
                "blue": "rgba(0, 0, 255, 0.3)",
                "green": "rgba(0, 128, 0, 0.3)",
                "gold": "rgba(255, 215, 0, 0.3)",
                "orange": "rgba(255, 165, 0, 0.3)",
                "red": "rgba(255, 0, 0, 0.3)",
                "purple": "rgba(128, 0, 128, 0.3)"
            }
            fill_color = color_map.get(color, "rgba(128, 128, 128, 0.3)")
            
            # 1. Shoreline Position Change
            fig.add_trace(
                go.Scatter(
                    x=hist_metrics['year'],
                    y=hist_metrics['change_m'],
                    mode='lines+markers',
                    name='Historical',
                    line=dict(color='blue', width=2),
                    marker=dict(size=8),
                    hovertemplate='<b>Year:</b> %{x}<br><b>Change:</b> %{y:.2f}m<extra></extra>'
                ),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Scatter(
                    x=pred_metrics['year'],
                    y=pred_metrics['change_m'],
                    mode='lines+markers',
                    name='Predicted',
                    line=dict(color=color, width=2, dash='dash'),
                    marker=dict(size=8, symbol='x'),
                    hovertemplate='<b>Year:</b> %{x}<br><b>Predicted:</b> %{y:.2f}m<extra></extra>'
                ),
                row=1, col=1
            )
            
            # Add zero line
            fig.add_hline(y=0, line_dash="dash", line_color="gray", line_width=1, row=1, col=1)
            
            # 2. Shoreline Length Over Time
            fig.add_trace(
                go.Scatter(
                    x=hist_metrics['year'],
                    y=hist_metrics['length'],
                    mode='lines+markers',
                    name='Historical Length',
                    line=dict(color='blue', width=2),
                    marker=dict(size=8),
                    showlegend=False,
                    hovertemplate='<b>Year:</b> %{x}<br><b>Length:</b> %{y:.2f}<extra></extra>'
                ),
                row=1, col=2
            )
            
            fig.add_trace(
                go.Scatter(
                    x=pred_metrics['year'],
                    y=pred_metrics['length'],
                    mode='lines+markers',
                    name='Predicted Length',
                    line=dict(color=color, width=2, dash='dash'),
                    marker=dict(size=8, symbol='x'),
                    showlegend=False,
                    hovertemplate='<b>Year:</b> %{x}<br><b>Length:</b> %{y:.2f}<extra></extra>'
                ),
                row=1, col=2
            )
            
            # 3. Rate of Change Analysis (bar chart)
            if len(hist_metrics) > 1:
                hist_rate = (hist_metrics['change_m'].iloc[-1] - hist_metrics['change_m'].iloc[0]) / (hist_metrics['year'].iloc[-1] - hist_metrics['year'].iloc[0])
            else:
                hist_rate = 0
            
            if len(pred_metrics) > 1:
                pred_rate = (pred_metrics['change_m'].iloc[-1] - pred_metrics['change_m'].iloc[0]) / (pred_metrics['year'].iloc[-1] - pred_metrics['year'].iloc[0])
            else:
                pred_rate = 0
            
            fig.add_trace(
                go.Bar(
                    x=['Historical Rate', 'Predicted Rate'],
                    y=[hist_rate, pred_rate],
                    marker_color=['blue', color],
                    text=[f'{hist_rate:.2f} m/yr', f'{pred_rate:.2f} m/yr'],
                    textposition='outside',
                    showlegend=False,
                    hovertemplate='<b>%{x}</b><br>Rate: %{y:.2f} m/yr<extra></extra>'
                ),
                row=2, col=1
            )
            
            # 4. Cumulative Change Projection (combined historical + prediction)
            combined_years = list(hist_metrics['year']) + list(pred_metrics['year'])
            combined_change = list(hist_metrics['change_m']) + list(pred_metrics['change_m'])
            
            fig.add_trace(
                go.Scatter(
                    x=combined_years,
                    y=combined_change,
                    mode='lines',
                    fill='tozeroy',
                    fillcolor=fill_color,
                    line=dict(color=color, width=2),
                    name='Cumulative Change',
                    showlegend=False,
                    hovertemplate='<b>Year:</b> %{x}<br><b>Change:</b> %{y:.2f}m<extra></extra>'
                ),
                row=2, col=2
            )
            
            # Add vertical line to separate historical and prediction
            if len(hist_metrics) > 0:
                last_hist_year = hist_metrics['year'].iloc[-1]
                fig.add_vline(x=last_hist_year, line_dash="dash", line_color="red", 
                             line_width=2, row=2, col=2,
                             annotation_text="Prediction Start",
                             annotation_position="top")
            
            # Update axes labels
            fig.update_xaxes(title_text="Year", row=1, col=1)
            fig.update_yaxes(title_text="Position Change (m)", row=1, col=1)
            
            fig.update_xaxes(title_text="Year", row=1, col=2)
            fig.update_yaxes(title_text="Shoreline Length", row=1, col=2)
            
            fig.update_xaxes(title_text="Period", row=2, col=1)
            fig.update_yaxes(title_text="Rate (m/year)", row=2, col=1)
            
            fig.update_xaxes(title_text="Year", row=2, col=2)
            fig.update_yaxes(title_text="Cumulative Change (m)", row=2, col=2)
            
            # Update layout
            fig.update_layout(
                height=800,
                showlegend=True,
                paper_bgcolor='#ffffff',
                plot_bgcolor='#ffffff',
                font=dict(color='#000000', size=12),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.15,
                    xanchor="center",
                    x=0.5,
                    bgcolor="rgba(255, 255, 255, 0.95)",
                    bordercolor="#d0d5dd",
                    borderwidth=2,
                    font=dict(color='#000000')
                ),
                hovermode='closest'
            )
            
            # Update all subplot backgrounds and grids
            for i in range(1, 3):
                for j in range(1, 3):
                    fig.update_xaxes(
                        showgrid=True,
                        gridcolor='#e9ecef',
                        gridwidth=1,
                        title_font=dict(color='#000000'),
                        tickfont=dict(color='#000000'),
                        row=i, col=j
                    )
                    fig.update_yaxes(
                        showgrid=True,
                        gridcolor='#e9ecef',
                        gridwidth=1,
                        title_font=dict(color='#000000'),
                        tickfont=dict(color='#000000'),
                        row=i, col=j
                    )
            
            # Display the chart
            st.plotly_chart(fig, use_container_width=True, config={
                'displayModeBar': True,
                'displaylogo': False,
                'modeBarButtonsToRemove': ['lasso2d', 'select2d']
            })
            
            # Display summary metrics
            st.markdown('<h4 style="margin-top: 1.5rem;">📊 Prediction Summary</h4>', unsafe_allow_html=True)
            
            metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
            
            with metric_col1:
                st.metric(
                    "Historical Period",
                    f"{hist_metrics['year'].iloc[0]:.0f}-{hist_metrics['year'].iloc[-1]:.0f}",
                    f"{hist_metrics['change_m'].iloc[-1]:.2f}m"
                )
            
            with metric_col2:
                st.metric(
                    "Prediction Period",
                    f"{pred_metrics['year'].iloc[0]:.0f}-{pred_metrics['year'].iloc[-1]:.0f}",
                    f"{pred_metrics['change_m'].iloc[-1] - pred_metrics['change_m'].iloc[0]:.2f}m"
                )
            
            with metric_col3:
                st.metric(
                    "Historical Rate",
                    f"{hist_rate:.2f} m/yr"
                )
            
            with metric_col4:
                st.metric(
                    "Predicted Rate",
                    f"{pred_rate:.2f} m/yr",
                    f"{pred_rate - hist_rate:+.2f} m/yr"
                )
            
            # Trend analysis
            st.markdown('<h4 style="margin-top: 1rem;">📈 Trend Analysis</h4>', unsafe_allow_html=True)
            
            if pred_rate > hist_rate:
                trend = "⬆️ Accelerating Change"
                trend_color = "red"
                trend_desc = f"The rate of shoreline change is predicted to increase by {abs(pred_rate - hist_rate):.2f} m/yr under {selected_slr} scenario."
            elif pred_rate < hist_rate:
                trend = "⬇️ Decelerating Change"
                trend_color = "green"
                trend_desc = f"The rate of shoreline change is predicted to decrease by {abs(pred_rate - hist_rate):.2f} m/yr under {selected_slr} scenario."
            else:
                trend = "➡️ Stable Trend"
                trend_color = "blue"
                trend_desc = f"The rate of shoreline change is predicted to remain stable under {selected_slr} scenario."
            
            st.markdown(f"**Trend:** <span style='color: {trend_color}; font-weight: bold;'>{trend}</span>", unsafe_allow_html=True)
            st.markdown(trend_desc)
            
        except Exception as e:
            st.error(f"❌ Error loading data: {str(e)}")
            import traceback
            with st.expander("Show detailed error"):
                st.code(traceback.format_exc())
    else:
        st.warning(f"""
        ⚠️ **Shapefiles not found!**
        
        Please create the following folder structure:
        
        ```
        data/Prediction/{method}/{site}/
        ├── SLR_0_1m/
        │   ├── shorelines_2019_2024.shp
        │   └── shorelines_2025_2100.shp
        ├── SLR_0_2m/
        │   ├── shorelines_2019_2024.shp
        │   └── shorelines_2025_2100.shp
        ├── SLR_0_3m/
        │   ├── shorelines_2019_2024.shp
        │   └── shorelines_2025_2100.shp
        ├── SLR_0_5m/
        │   ├── shorelines_2019_2024.shp
        │   └── shorelines_2025_2100.shp
        └── SLR_1_0m/
            ├── shorelines_2019_2024.shp
            └── shorelines_2025_2100.shp
        ```
        
        Missing files:
        - Historical: {'✓' if historical_path.exists() else '❌'}
        - Prediction: {'✓' if prediction_path.exists() else '❌'}
        """)
