import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from pathlib import Path

def render_column4_microsoft(method, site):
    """Render summary statistics plots for Column 4 - Microsoft Method"""
    
    st.markdown('<h3>📊 Summary Statistics - Microsoft</h3>', unsafe_allow_html=True)
    
    csv_path = Path(f"data/Microsoft/{site}/Column1Graph")
    transect_stats_path = csv_path / "transect_statistics.csv"
    
    if not transect_stats_path.exists():
        st.warning(f"""
        ⚠️ **Data file not found!**
        
        Please ensure the following file exists:
        - {transect_stats_path}
        """)
        return
    
    try:
        transect_stats = pd.read_csv(transect_stats_path)
        
        # Create figure với màu sắc khác để phân biệt
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Net Coastal Change by Transect (Microsoft)',
                'Annual Rate of Change (Microsoft)',
                'Maximum Erosion vs Accretion (Microsoft)',
                'Mean Change ± Std Dev (Microsoft)'
            ),
            specs=[[{"type": "bar"}, {"type": "bar"}],
                   [{"type": "bar"}, {"type": "scatter"}]],
            vertical_spacing=0.12,
            horizontal_spacing=0.1
        )
        
        transects = transect_stats['Transect'].tolist()
        
        # 1. Net Coastal Change (màu khác)
        colors_net = ['#e74c3c' if x < 0 else '#3498db' 
                      for x in transect_stats['Net_Change_m']]
        
        fig.add_trace(
            go.Bar(
                x=transects,
                y=transect_stats['Net_Change_m'],
                marker_color=colors_net,
                text=[f"{val:.1f}m" for val in transect_stats['Net_Change_m']],
                textposition='outside',
                showlegend=False,
                hovertemplate='<b>%{x}</b><br>Net Change: %{y:.2f}m<extra></extra>'
            ),
            row=1, col=1
        )
        
        # 2. Annual Rate
        colors_rate = ['#e74c3c' if x < 0 else '#3498db' 
                       for x in transect_stats['Rate_m_per_year']]
        
        fig.add_trace(
            go.Bar(
                x=transects,
                y=transect_stats['Rate_m_per_year'],
                marker_color=colors_rate,
                showlegend=False,
                hovertemplate='<b>%{x}</b><br>Rate: %{y:.2f}m/year<extra></extra>'
            ),
            row=1, col=2
        )
        
        # 3. Erosion vs Accretion
        fig.add_trace(
            go.Bar(
                x=transects,
                y=transect_stats['Max_Erosion_m'],
                name='Max Erosion',
                marker_color='#e74c3c',
                hovertemplate='<b>%{x}</b><br>Max Erosion: %{y:.2f}m<extra></extra>'
            ),
            row=2, col=1
        )
        
        fig.add_trace(
            go.Bar(
                x=transects,
                y=transect_stats['Max_Accretion_m'],
                name='Max Accretion',
                marker_color='#3498db',
                hovertemplate='<b>%{x}</b><br>Max Accretion: %{y:.2f}m<extra></extra>'
            ),
            row=2, col=1
        )
        
        # 4. Mean ± Std Dev
        fig.add_trace(
            go.Scatter(
                x=transects,
                y=transect_stats['Mean_Change_m'],
                mode='lines+markers',
                name='Mean Change',
                line=dict(color='#9b59b6', width=2),
                marker=dict(size=10),
                error_y=dict(
                    type='data',
                    array=transect_stats['Std_Dev_m'],
                    visible=True,
                    color='#95a5a6',
                    thickness=2,
                    width=6
                ),
                hovertemplate='<b>%{x}</b><br>Mean: %{y:.2f}m<extra></extra>'
            ),
            row=2, col=2
        )
        
        fig.add_hline(y=0, line_dash="dash", line_color="black", 
                     line_width=1, row=2, col=2)
        
        # Update axes
        fig.update_xaxes(title_text="Transect", row=1, col=1)
        fig.update_xaxes(title_text="Transect", row=1, col=2)
        fig.update_xaxes(title_text="Transect", row=2, col=1)
        fig.update_xaxes(title_text="Transect", row=2, col=2)
        
        fig.update_yaxes(title_text="Net Change (m)", row=1, col=1)
        fig.update_yaxes(title_text="Rate (m/year)", row=1, col=2)
        fig.update_yaxes(title_text="Distance (m)", row=2, col=1)
        fig.update_yaxes(title_text="Mean Change (m)", row=2, col=2)
        
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
        
        fig.add_hline(y=0, line_dash="solid", line_color="black", 
                     line_width=1, row=1, col=1)
        fig.add_hline(y=0, line_dash="solid", line_color="black", 
                     line_width=1, row=1, col=2)
        
        st.plotly_chart(fig, use_container_width=True, config={
            'displayModeBar': True,
            'displaylogo': False,
            'modeBarButtonsToRemove': ['lasso2d', 'select2d']
        })
        
        # Individual plots section (tương tự column4.py)
        st.markdown('<h4 style="margin-top: 1.5rem;">🔍 View Individual Plots</h4>', unsafe_allow_html=True)
        
        col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 0.5])
        
        with col1:
            if st.button("📊 Net Change", use_container_width=True, key="ms_net"):
                st.session_state['selected_plot_ms'] = 'net_change'
        
        with col2:
            if st.button("📈 Rate of Change", use_container_width=True, key="ms_rate"):
                st.session_state['selected_plot_ms'] = 'rate'
        
        with col3:
            if st.button("⚖️ Erosion vs Accretion", use_container_width=True, key="ms_erosion"):
                st.session_state['selected_plot_ms'] = 'erosion_accretion'
        
        with col4:
            if st.button("📉 Mean ± Std Dev", use_container_width=True, key="ms_mean"):
                st.session_state['selected_plot_ms'] = 'mean_std'
        
        with col5:
            if st.button("❌", use_container_width=True, help="Close individual plot", key="ms_close"):
                if 'selected_plot_ms' in st.session_state:
                    del st.session_state['selected_plot_ms']
                    st.rerun()
        
        # Render individual plots (tương tự column4.py nhưng với key khác)
        if 'selected_plot_ms' in st.session_state:
            selected = st.session_state['selected_plot_ms']
            
            if selected == 'net_change':
                fig_individual = go.Figure()
                fig_individual.add_trace(go.Bar(
                    x=transects,
                    y=transect_stats['Net_Change_m'],
                    marker_color=colors_net,
                    text=[f"{val:.1f}m" for val in transect_stats['Net_Change_m']],
                    textposition='outside',
                    hovertemplate='<b>%{x}</b><br>Net Change: %{y:.2f}m<extra></extra>'
                ))
                fig_individual.update_layout(
                    title="Net Coastal Change by Transect (Microsoft)",
                    xaxis_title="Transect",
                    yaxis_title="Net Change (m)",
                    height=500,
                    paper_bgcolor='#ffffff',
                    plot_bgcolor='#ffffff',
                    font=dict(color='#000000', size=12),
                    title_font=dict(color='#000000', size=14),
                    xaxis=dict(showgrid=True, gridcolor='#e9ecef', title_font=dict(color='#000000'), tickfont=dict(color='#000000')),
                    yaxis=dict(showgrid=True, gridcolor='#e9ecef', title_font=dict(color='#000000'), tickfont=dict(color='#000000'))
                )
                fig_individual.add_hline(y=0, line_dash="solid", line_color="black", line_width=1)
                st.plotly_chart(fig_individual, use_container_width=True)
            
            # Thêm các plot khác tương tự...
        
    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")
        import traceback
        with st.expander("Show detailed error"):
            st.code(traceback.format_exc())