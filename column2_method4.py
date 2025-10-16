import streamlit as st
import plotly.graph_objects as go
import geopandas as gpd
import pandas as pd
from pathlib import Path

def render_column2_method4(method, site):
    """Render interactive map for Column 2 - Method 4 (Sea Level Rise)"""
    
    st.markdown('<h3>📍 Bruun Rules Method</h3>', unsafe_allow_html=True)
    
    base_path = Path(f"data/Method4/{site}")
    
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
        key="slr_scenario_selector"
    )
    
    slr_folder = slr_scenarios[selected_slr]
    
    # Paths
    shorelines_path = base_path / slr_folder / "shorelines_2019_2024.shp"
    
    files_exist = shorelines_path.exists()
    
    if files_exist:
        try:
            # Cache the loading and processing of shapefiles
            @st.cache_data
            def load_and_process_shapefiles(shorelines_path):
                # Load shapefiles
                shorelines = gpd.read_file(shorelines_path)
                
                # Remove rows with None geometry
                shorelines = shorelines[shorelines.geometry.notna()]
                
                # Convert to WGS84 if needed
                if shorelines.crs != "EPSG:4326":
                    shorelines = shorelines.to_crs("EPSG:4326")
                
                return shorelines
            
            # Load data
            shorelines = load_and_process_shapefiles(str(shorelines_path))
            
            # Auto-detect year field
            def find_year_field(gdf, possible_names):
                for name in possible_names:
                    if name in gdf.columns:
                        return name
                return None
            
            year_field = find_year_field(shorelines, ['year', 'Year', 'YEAR'])
            
            if not year_field:
                st.error(f"""
                ❌ **Cannot find year field in shorelines shapefile!**
                
                Expected fields: 'year', 'Year', or 'YEAR'
                """)
            else:
                # Get year range
                years = sorted(shorelines[year_field].unique())
                
                if len(years) > 0:
                    # Calculate initial center (FIXED - không thay đổi)
                    all_data = shorelines.geometry
                    all_data = all_data[all_data.notna()]
                    bounds = all_data.total_bounds
                    default_center_lon = (bounds[0] + bounds[2]) / 2
                    default_center_lat = (bounds[1] + bounds[3]) / 2
                    
                    # Create figure
                    fig = go.Figure()
                    
                    # Color mapping for different SLR scenarios
                    slr_colors = {
                        "0.1m Sea Level Rise": "blue",
                        "0.2m Sea Level Rise": "green",
                        "0.3m Sea Level Rise": "gold",
                        "0.5m Sea Level Rise": "orange",
                        "1.0m Sea Level Rise": "red"
                    }
                    
                    shoreline_color = slr_colors.get(selected_slr, "purple")
                    
                    # Add dummy trace for legend
                    fig.add_trace(go.Scattermapbox(
                        lon=[default_center_lon],
                        lat=[default_center_lat],
                        mode='lines',
                        line=dict(width=3, color=shoreline_color),
                        name=f'Shorelines ({selected_slr})',
                        showlegend=True,
                        visible=True,
                        legendgroup='shorelines',
                        hoverinfo='skip'
                    ))
                    
                    # Create frames for each year
                    frames = []
                    
                    for year_idx, year in enumerate(years):
                        frame_data = []
                        
                        # Keep dummy trace
                        frame_data.append(go.Scattermapbox(
                            lon=[default_center_lon],
                            lat=[default_center_lat],
                            mode='lines',
                            line=dict(width=3, color=shoreline_color),
                            name=f'Shorelines ({selected_slr})',
                            showlegend=True,
                            visible=True,
                            legendgroup='shorelines',
                            hoverinfo='skip'
                        ))
                        
                        # Filter shorelines for this year
                        shorelines_year = shorelines[shorelines[year_field] == year]
                        
                        # Add shorelines for this year
                        if not shorelines_year.empty:
                            for idx, row in shorelines_year.iterrows():
                                geom = row.geometry
                                if geom is None:
                                    continue
                                
                                hover_text = f"<b>Shoreline ({selected_slr})</b><br>"
                                for col in shorelines_year.columns:
                                    if col != 'geometry':
                                        hover_text += f"{col}: {row[col]}<br>"
                                
                                if geom.geom_type == 'LineString':
                                    x, y = geom.xy
                                    frame_data.append(go.Scattermapbox(
                                        lon=list(x),
                                        lat=list(y),
                                        mode='lines',
                                        line=dict(width=3, color=shoreline_color),
                                        showlegend=False,
                                        hovertemplate=hover_text + '<extra></extra>',
                                        legendgroup='shorelines'
                                    ))
                                elif geom.geom_type == 'MultiLineString':
                                    for line in geom.geoms:
                                        x, y = line.xy
                                        frame_data.append(go.Scattermapbox(
                                            lon=list(x),
                                            lat=list(y),
                                            mode='lines',
                                            line=dict(width=3, color=shoreline_color),
                                            showlegend=False,
                                            hovertemplate=hover_text + '<extra></extra>',
                                            legendgroup='shorelines'
                                        ))
                        
                        # BỎ layout trong frame - giống column1.py
                        frames.append(go.Frame(
                            data=frame_data,
                            name=str(year)
                        ))
                    
                    # Add initial data for last year
                    last_year = years[-1]
                    shorelines_last = shorelines[shorelines[year_field] == last_year]
                    
                    # Add shorelines
                    if not shorelines_last.empty:
                        for idx, row in shorelines_last.iterrows():
                            geom = row.geometry
                            if geom is None:
                                continue
                            
                            hover_text = f"<b>Shoreline ({selected_slr})</b><br>"
                            for col in shorelines_last.columns:
                                if col != 'geometry':
                                    hover_text += f"{col}: {row[col]}<br>"
                            
                            if geom.geom_type == 'LineString':
                                x, y = geom.xy
                                fig.add_trace(go.Scattermapbox(
                                    lon=list(x),
                                    lat=list(y),
                                    mode='lines',
                                    line=dict(width=3, color=shoreline_color),
                                    showlegend=False,
                                    hovertemplate=hover_text + '<extra></extra>',
                                    legendgroup='shorelines'
                                ))
                            elif geom.geom_type == 'MultiLineString':
                                for line in geom.geoms:
                                    x, y = line.xy
                                    fig.add_trace(go.Scattermapbox(
                                        lon=list(x),
                                        lat=list(y),
                                        mode='lines',
                                        line=dict(width=3, color=shoreline_color),
                                        showlegend=False,
                                        hovertemplate=hover_text + '<extra></extra>',
                                        legendgroup='shorelines'
                                    ))
                    
                    # Add frames to figure
                    fig.frames = frames
                    
                    # Update layout - giống column1.py
                    fig.update_layout(
                        mapbox=dict(
                            style="open-street-map",
                            center=dict(lon=default_center_lon, lat=default_center_lat),
                            zoom=13
                        ),
                        height=600,
                        margin=dict(l=0, r=0, t=0, b=0),
                        showlegend=True,
                        paper_bgcolor='#ffffff',
                        plot_bgcolor='#ffffff',
                        font=dict(color='#000000', size=12),
                        legend=dict(
                            yanchor="top",
                            y=0.99,
                            xanchor="left",
                            x=0.01,
                            bgcolor="rgba(255, 255, 255, 0.95)",
                            font=dict(color="#000000", size=12),
                            bordercolor="#d0d5dd",
                            borderwidth=2
                        ),
                        updatemenus=[{
                            'type': 'buttons',
                            'showactive': False,
                            'bgcolor': '#ffffff',
                            'bordercolor': '#d0d5dd',
                            'borderwidth': 2,
                            'font': dict(color='#000000'),
                            'buttons': [
                                {
                                    'label': '▶ Play',
                                    'method': 'animate',
                                    'args': [None, {
                                        'frame': {'duration': 1000, 'redraw': True},
                                        'fromcurrent': True,
                                        'mode': 'immediate',
                                        'transition': {'duration': 300}
                                    }]
                                },
                                {
                                    'label': '⏸ Pause',
                                    'method': 'animate',
                                    'args': [[None], {
                                        'frame': {'duration': 0, 'redraw': False},
                                        'mode': 'immediate',
                                        'transition': {'duration': 0}
                                    }]
                                }
                            ],
                            'x': 0.1,
                            'y': 0,
                            'xanchor': 'left',
                            'yanchor': 'bottom'
                        }],
                        sliders=[{
                            'active': len(years) - 1,
                            'bgcolor': '#ffffff',
                            'bordercolor': '#d0d5dd',
                            'borderwidth': 2,
                            'tickcolor': '#000000',
                            'font': dict(color='#000000'),
                            'steps': [
                                {
                                    'args': [[f.name], {
                                        'frame': {'duration': 0, 'redraw': True},
                                        'mode': 'immediate',
                                        'transition': {'duration': 0}
                                    }],
                                    'label': str(year),
                                    'method': 'animate'
                                }
                                for f, year in zip(frames, years)
                            ],
                            'x': 0.1,
                            'y': 0,
                            'len': 0.85,
                            'xanchor': 'left',
                            'yanchor': 'top',
                            'pad': {'b': 10, 't': 50},
                            'currentvalue': {
                                'visible': True,
                                'prefix': 'Year: ',
                                'xanchor': 'right',
                                'font': {'size': 16, 'color': '#000000'}
                            }
                        }]
                    )
                    
                    # Render the chart
                    st.plotly_chart(
                        fig, 
                        use_container_width=True, 
                        config={
                            'scrollZoom': True,
                            'displayModeBar': True,
                            'displaylogo': False,
                            'modeBarButtonsToRemove': ['lasso2d', 'select2d']
                        }
                    )
                    
                else:
                    st.warning("⚠️ No valid years found in the data.")
                
        except Exception as e:
            st.error(f"❌ Error loading shapefiles: {str(e)}")
            import traceback
            with st.expander("Show detailed error"):
                st.code(traceback.format_exc())
    else:
        st.warning(f"""
        ⚠️ **Shapefiles not found!**
        
        Please create the following folder structure:
        
        ```
        data/Method4/{site}/
        ├── SLR_0_1m/shorelines_2019_2024.shp
        ├── SLR_0_2m/shorelines_2019_2024.shp
        ├── SLR_0_3m/shorelines_2019_2024.shp
        ├── SLR_0_5m/shorelines_2019_2024.shp
        └── SLR_1_0m/shorelines_2019_2024.shp
        ```
        
        Missing files:
        - Shorelines ({slr_folder}): {'✓' if shorelines_path.exists() else '❌'}
        """)
