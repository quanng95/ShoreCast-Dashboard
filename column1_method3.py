import streamlit as st
import plotly.graph_objects as go
import geopandas as gpd
import pandas as pd
from pathlib import Path

def render_column1_method3(method, site):
    """Render interactive map for Column 1 - Method 3 (only shorelines and transects)"""
    
    st.markdown('<h3>📍 Best Curve Fitting Method (Sentinel Satelittes)</h3>', unsafe_allow_html=True)
    
    base_path = Path(f"data/Method3/{site}")
    
    shorelines_path = base_path / f"{site}_shorelines.shp"
    transects_path = base_path / f"{site}_transects.shp"
    
    files_exist = all([
        shorelines_path.exists(),
        transects_path.exists()
    ])
    
    if files_exist:
        try:
            # Cache the loading and processing of shapefiles
            @st.cache_data
            def load_and_process_shapefiles(shorelines_path, transects_path):
                # Load shapefiles
                shorelines = gpd.read_file(shorelines_path)
                transects = gpd.read_file(transects_path)
                
                # Remove rows with None geometry
                shorelines = shorelines[shorelines.geometry.notna()]
                transects = transects[transects.geometry.notna()]
                
                # Convert to WGS84 if needed
                if shorelines.crs != "EPSG:4326":
                    shorelines = shorelines.to_crs("EPSG:4326")
                if transects.crs != "EPSG:4326":
                    transects = transects.to_crs("EPSG:4326")
                
                return shorelines, transects
            
            # Load data once
            shorelines, transects = load_and_process_shapefiles(
                str(shorelines_path), str(transects_path)
            )
            
            # Auto-detect year field names
            def find_year_field(gdf, possible_names):
                for name in possible_names:
                    if name in gdf.columns:
                        return name
                return None
            
            year_field_shorelines = find_year_field(shorelines, ['year', 'Year', 'YEAR', 'date', 'Date'])
            
            # Check if year fields are found
            if not year_field_shorelines:
                st.error(f"""
                ❌ **Cannot find year field in shorelines shapefile!**
                
                Expected fields: 'year', 'Year', 'YEAR', 'date', or 'Date'
                """)
            else:
                # Get year range
                years_shorelines = sorted(shorelines[year_field_shorelines].unique())
                
                if len(years_shorelines) > 0:
                    # Calculate initial center
                    all_data = pd.concat([
                        shorelines.geometry,
                        transects.geometry
                    ])
                    all_data = all_data[all_data.notna()]
                    bounds = all_data.total_bounds
                    default_center_lon = (bounds[0] + bounds[2]) / 2
                    default_center_lat = (bounds[1] + bounds[3]) / 2
                    
                    # Create figure
                    fig = go.Figure()
                    
                    # Add dummy traces for legend (màu vàng/cam cho Method 3)
                    fig.add_trace(go.Scattermapbox(
                        lon=[default_center_lon],
                        lat=[default_center_lat],
                        mode='lines',
                        line=dict(width=2, color='rgba(255, 193, 7, 0.5)'),  # Vàng
                        name='Transects',
                        showlegend=True,
                        visible=True,
                        legendgroup='transects',
                        hoverinfo='skip'
                    ))
                    
                    fig.add_trace(go.Scattermapbox(
                        lon=[default_center_lon],
                        lat=[default_center_lat],
                        mode='lines',
                        line=dict(width=2, color='darkred'),  # Cam đậm
                        name='Shorelines',
                        showlegend=True,
                        visible=True,
                        legendgroup='shorelines',
                        hoverinfo='skip'
                    ))
                    
                    # Create frames for each year
                    frames = []
                    
                    for year_idx, year in enumerate(years_shorelines):
                        frame_data = []
                        
                        # Keep dummy traces in frames (first 2 traces)
                        frame_data.append(go.Scattermapbox(
                            lon=[default_center_lon],
                            lat=[default_center_lat],
                            mode='lines',
                            line=dict(width=2, color='rgba(255, 193, 7, 0.5)'),
                            name='Transects',
                            showlegend=True,
                            visible=True,
                            legendgroup='transects',
                            hoverinfo='skip'
                        ))
                        
                        frame_data.append(go.Scattermapbox(
                            lon=[default_center_lon],
                            lat=[default_center_lat],
                            mode='lines',
                            line=dict(width=2, color='darkred'),
                            name='Shorelines',
                            showlegend=True,
                            visible=True,
                            legendgroup='shorelines',
                            hoverinfo='skip'
                        ))
                        
                        # Filter data for this year
                        shorelines_year = shorelines[shorelines[year_field_shorelines] == year]
                        
                        # Add transects (same for all years)
                        if not transects.empty:
                            for idx, row in transects.iterrows():
                                geom = row.geometry
                                if geom is None:
                                    continue
                                
                                hover_text = "<b>Transect (Method 3)</b><br>"
                                for col in transects.columns:
                                    if col != 'geometry':
                                        hover_text += f"{col}: {row[col]}<br>"
                                
                                if geom.geom_type == 'LineString':
                                    x, y = geom.xy
                                    frame_data.append(go.Scattermapbox(
                                        lon=list(x),
                                        lat=list(y),
                                        mode='lines',
                                        line=dict(width=2, color='rgba(255, 193, 7, 0.5)'),
                                        showlegend=False,
                                        hovertemplate=hover_text + '<extra></extra>',
                                        legendgroup='transects'
                                    ))
                                elif geom.geom_type == 'MultiLineString':
                                    for line in geom.geoms:
                                        x, y = line.xy
                                        frame_data.append(go.Scattermapbox(
                                            lon=list(x),
                                            lat=list(y),
                                            mode='lines',
                                            line=dict(width=2, color='rgba(255, 193, 7, 0.5)'),
                                            showlegend=False,
                                            hovertemplate=hover_text + '<extra></extra>',
                                            legendgroup='transects'
                                        ))
                        
                        # Add shorelines for this year
                        if not shorelines_year.empty:
                            for idx, row in shorelines_year.iterrows():
                                geom = row.geometry
                                if geom is None:
                                    continue
                                
                                hover_text = "<b>Shoreline (Method 3)</b><br>"
                                for col in shorelines_year.columns:
                                    if col != 'geometry':
                                        hover_text += f"{col}: {row[col]}<br>"
                                
                                if geom.geom_type == 'LineString':
                                    x, y = geom.xy
                                    frame_data.append(go.Scattermapbox(
                                        lon=list(x),
                                        lat=list(y),
                                        mode='lines',
                                        line=dict(width=2, color='darkred'),
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
                                            line=dict(width=2, color='darkred'),
                                            showlegend=False,
                                            hovertemplate=hover_text + '<extra></extra>',
                                            legendgroup='shorelines'
                                        ))
                        
                        frames.append(go.Frame(
                            data=frame_data,
                            name=str(year)
                        ))
                    
                    # Add initial data for last year
                    last_year = years_shorelines[-1]
                    shorelines_last = shorelines[shorelines[year_field_shorelines] == last_year]
                    
                    # Add transects
                    if not transects.empty:
                        for idx, row in transects.iterrows():
                            geom = row.geometry
                            if geom is None:
                                continue
                            
                            hover_text = "<b>Transect (Method 3)</b><br>"
                            for col in transects.columns:
                                if col != 'geometry':
                                    hover_text += f"{col}: {row[col]}<br>"
                            
                            if geom.geom_type == 'LineString':
                                x, y = geom.xy
                                fig.add_trace(go.Scattermapbox(
                                    lon=list(x),
                                    lat=list(y),
                                    mode='lines',
                                    line=dict(width=2, color='rgba(255, 193, 7, 0.5)'),
                                    showlegend=False,
                                    hovertemplate=hover_text + '<extra></extra>',
                                    legendgroup='transects'
                                ))
                            elif geom.geom_type == 'MultiLineString':
                                for line in geom.geoms:
                                    x, y = line.xy
                                    fig.add_trace(go.Scattermapbox(
                                        lon=list(x),
                                        lat=list(y),
                                        mode='lines',
                                        line=dict(width=2, color='rgba(255, 193, 7, 0.5)'),
                                        showlegend=False,
                                        hovertemplate=hover_text + '<extra></extra>',
                                        legendgroup='transects'
                                    ))
                    
                    # Add shorelines
                    if not shorelines_last.empty:
                        for idx, row in shorelines_last.iterrows():
                            geom = row.geometry
                            if geom is None:
                                continue
                            
                            hover_text = "<b>Shoreline (Method 3)</b><br>"
                            for col in shorelines_last.columns:
                                if col != 'geometry':
                                    hover_text += f"{col}: {row[col]}<br>"
                            
                            if geom.geom_type == 'LineString':
                                x, y = geom.xy
                                fig.add_trace(go.Scattermapbox(
                                    lon=list(x),
                                    lat=list(y),
                                    mode='lines',
                                    line=dict(width=2, color='darkred'),
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
                                        line=dict(width=2, color='darkred'),
                                        showlegend=False,
                                        hovertemplate=hover_text + '<extra></extra>',
                                        legendgroup='shorelines'
                                    ))
                    
                    # Add frames to figure
                    fig.frames = frames
                    
                    # Update layout with white background
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
                            'active': len(years_shorelines) - 1,
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
                                for f, year in zip(frames, years_shorelines)
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
        
        Please create the following folder structure and add your shapefiles:
        
        ```
        data/
        └── Method3/
            └── {site}/
                ├── {site}_shorelines.shp
                └── {site}_transects.shp
        ```
        
        Missing files:
        - Shorelines: {'✓' if shorelines_path.exists() else '❌'}
        - Transects: {'✓' if transects_path.exists() else '❌'}
        """)
