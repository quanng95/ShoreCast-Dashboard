import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from pathlib import Path

def render_column3_microsoft(method, site):
    """Render time series plots for Column 3 - Microsoft Method"""
    
    st.markdown('<h3>📈 Time Series Analysis - Microsoft</h3>', unsafe_allow_html=True)
    
    # Load CSV data từ folder Microsoft
    csv_path = Path(f"data/Microsoft/{site}/Column1Graph")
    
    # Check for required files
    transect_stats_path = csv_path / "transect_statistics.csv"
    time_series_path = csv_path / "time_series_data.csv"
    
    if not transect_stats_path.exists() or not time_series_path.exists():
        st.warning(f"""
        ⚠️ **Data files not found!**
        
        Please ensure the following files exist:
        - {transect_stats_path}
        - {time_series_path}
        
        Expected folder structure:
        ```
        data/
        └── Microsoft/
            └── {site}/
                └── Column1Graph/
                    ├── transect_statistics.csv
                    └── time_series_data.csv
        ```
        """)
        return
    
    try:
        # Load data
        transect_stats = pd.read_csv(transect_stats_path)
        time_series = pd.read_csv(time_series_path)
        
        # Convert dates column to datetime
        time_series['dates'] = pd.to_datetime(time_series['dates'])
        
        # Get list of transects
        transects = [col for col in time_series.columns if col.endswith('_distance_m')]
        transect_names = [col.replace('_distance_m', '') for col in transects]
        
        # Create figure
        fig = go.Figure()
        
        # Add traces for each transect
        for i, (transect_col, transect_name) in enumerate(zip(transects, transect_names)):
            stats = transect_stats[transect_stats['Transect'] == transect_name].iloc[0]
            transect_data = time_series[['dates', 'year', transect_col]].dropna()
            
            if len(transect_data) > 0:
                first_value = transect_data[transect_col].iloc[0]
                cumulative_change = transect_data[transect_col] - first_value
            else:
                cumulative_change = []
            
            hover_text = [
                f"<b>Date:</b> {date.strftime('%Y-%m-%d')}<br>" +
                f"<b>Year:</b> {year}<br>" +
                f"<b>Distance:</b> {dist:.2f} m<br>" +
                f"<b>Change:</b> {change:.2f} m"
                for date, year, dist, change in zip(
                    transect_data['dates'], 
                    transect_data['year'],
                    transect_data[transect_col],
                    cumulative_change
                )
            ]
            
            accretion_mask = cumulative_change > 0
            erosion_mask = cumulative_change < 0
            
            # Add line trace
            fig.add_trace(go.Scatter(
                x=transect_data['dates'],
                y=cumulative_change,
                mode='lines+markers',
                name=transect_name,
                line=dict(width=2, color='#ff6b6b'),  # Đổi màu để phân biệt
                marker=dict(size=6),
                hovertemplate='%{text}<extra></extra>',
                text=hover_text,
                visible=(i == 0)
            ))
            
            # Add accretion area
            if accretion_mask.any():
                accretion_data = cumulative_change.copy()
                accretion_data[~accretion_mask] = 0
                
                fig.add_trace(go.Scatter(
                    x=transect_data['dates'],
                    y=accretion_data,
                    fill='tozeroy',
                    fillcolor='rgba(144, 238, 144, 0.3)',
                    line=dict(width=0),
                    showlegend=False,
                    hoverinfo='skip',
                    visible=(i == 0)
                ))
            
            # Add erosion area
            if erosion_mask.any():
                erosion_data = cumulative_change.copy()
                erosion_data[~erosion_mask] = 0
                
                fig.add_trace(go.Scatter(
                    x=transect_data['dates'],
                    y=erosion_data,
                    fill='tozeroy',
                    fillcolor='rgba(255, 182, 193, 0.3)',
                    line=dict(width=0),
                    showlegend=False,
                    hoverinfo='skip',
                    visible=(i == 0)
                ))
        
        # Create buttons
        buttons = []
        for i, transect_name in enumerate(transect_names):
            stats = transect_stats[transect_stats['Transect'] == transect_name].iloc[0]
            visible = [False] * len(fig.data)
            visible[i * 3] = True
            visible[i * 3 + 1] = True
            visible[i * 3 + 2] = True
            
            buttons.append(dict(
                label=f"{transect_name}",
                method="update",
                args=[
                    {"visible": visible},
                    {
                        "title": f"<b>Microsoft - {transect_name}</b> | Net: {stats['Net_Change_m']:.1f}m | " +
                                f"Rate: {stats['Rate_m_per_year']:.2f}m/yr | " +
                                f"Mean: {stats['Mean_Change_m']:.1f}±{stats['Std_Dev_m']:.1f}m"
                    }
                ]
            ))
        
        # Update layout
        first_transect = transect_stats.iloc[0]
        fig.update_layout(
            title=f"<b>Microsoft - {first_transect['Transect']}</b> | Net: {first_transect['Net_Change_m']:.1f}m | " +
                  f"Rate: {first_transect['Rate_m_per_year']:.2f}m/yr | " +
                  f"Mean: {first_transect['Mean_Change_m']:.1f}±{first_transect['Std_Dev_m']:.1f}m",
            xaxis_title="Date",
            yaxis_title="Change (m)",
            hovermode='closest',
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
            updatemenus=[
                dict(
                    type="dropdown",
                    direction="down",
                    x=0.02,
                    y=1.15,
                    xanchor="left",
                    yanchor="top",
                    buttons=buttons,
                    bgcolor="#ffffff",
                    bordercolor="#d0d5dd",
                    borderwidth=2,
                    font=dict(size=12, color='#000000')
                )
            ],
            xaxis=dict(
                showgrid=True,
                gridcolor='#e9ecef',
                gridwidth=1,
                zeroline=True,
                zerolinecolor='#000000',
                zerolinewidth=2,
                title_font=dict(color='#000000'),
                tickfont=dict(color='#000000')
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
        
        fig.add_hline(y=0, line_dash="dash", line_color="black", line_width=1)
        
        # Add legend entries
        fig.add_trace(go.Scatter(
            x=[None], y=[None],
            mode='markers',
            marker=dict(size=10, color='rgba(144, 238, 144, 0.5)'),
            showlegend=True,
            name='Accretion',
            hoverinfo='skip'
        ))
        
        fig.add_trace(go.Scatter(
            x=[None], y=[None],
            mode='markers',
            marker=dict(size=10, color='rgba(255, 182, 193, 0.5)'),
            showlegend=True,
            name='Erosion',
            hoverinfo='skip'
        ))
        
        st.plotly_chart(fig, use_container_width=True, config={
            'displayModeBar': True,
            'displaylogo': False,
            'modeBarButtonsToRemove': ['lasso2d', 'select2d']
        })
        
        # Display summary statistics
        st.markdown('<h4 style="margin-top: 1.5rem;">📊 Transect Statistics Summary</h4>', unsafe_allow_html=True)
        
        html_table = """
        <style>
        .custom-table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            font-size: 14px;
            background-color: white;
        }
        .custom-table thead tr {
            background-color: #f0f2f6;
            color: #000000;
            text-align: left;
            font-weight: bold;
        }
        .custom-table th,
        .custom-table td {
            padding: 12px 15px;
            border: 2px solid #000000;
            color: #000000;
        }
        .custom-table tbody tr {
            border-bottom: 2px solid #000000;
            background-color: white;
        }
        .custom-table tbody tr:hover {
            background-color: #f8f9fa;
        }
        </style>
        <div style="overflow-x: auto;">
        <table class="custom-table">
            <thead>
                <tr>
        """
        
        for col in transect_stats.columns:
            html_table += f"<th>{col}</th>"
        html_table += "</tr></thead><tbody>"
        
        for idx, row in transect_stats.iterrows():
            html_table += "<tr>"
            for col in transect_stats.columns:
                value = row[col]
                if col in ['Mean_Change_m', 'Std_Dev_m', 'Max_Erosion_m', 'Max_Accretion_m', 'Net_Change_m', 'Rate_m_per_year']:
                    value = f"{value:.2f}"
                html_table += f"<td>{value}</td>"
            html_table += "</tr>"
        
        html_table += "</tbody></table></div>"
        st.markdown(html_table, unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")
        import traceback
        with st.expander("Show detailed error"):
            st.code(traceback.format_exc())