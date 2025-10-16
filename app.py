import streamlit as st
from column1 import render_column1
from column2 import render_column2
from column3 import render_column3
from column4 import render_column4
# Import thêm các column cho phương pháp khác
from column3_microsoft import render_column3_microsoft
from column4_microsoft import render_column4_microsoft

# Import columns cho Method 3 và Method 4
from column1_method3 import render_column1_method3
from column2_method4 import render_column2_method4

# Import columns cho Prediction
from column5 import render_column5
from column6 import render_column6

# Import columns cho Planning and Mitigation
from column7 import render_column7
from column8 import render_column8

# Import columns cho Method 3
from column3_method3 import render_column3_method3
from column4_method3 import render_column4_method3

# Page configuration
st.set_page_config(
    page_title="SHORECAST - Coastal Shoreline Change Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for white theme with borders (giữ nguyên như cũ)
st.markdown("""
    <style>
    /* Force white background for everything */
    .stApp {
        background-color: #ffffff !important;
    }
    
    /* ==================== HEADER STYLING ==================== */
    
    /* Header background */
    header[data-testid="stHeader"] {
        background-color: #f0f2f6 !important;
        border-bottom: 2px solid #d0d5dd !important;
        height: 4.5rem !important;
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        right: 0 !important;
        z-index: 999 !important;
    }
    
    /* Hide default Streamlit header content */
    header[data-testid="stHeader"] > div:first-child {
        display: none !important;
    }
    
    /* Custom header title container with icon */
    header[data-testid="stHeader"]::before {
        content: "🌊 SHORECAST - Coastal Shoreline Monitoring & Predicting Dashboard";
        display: flex;
        align-items: center;
        justify-content: center;
        height: 100%;
        width: 100%;
        font-size: 1.8rem;
        font-weight: 700;
        color: #000000;
        background-color: #f0f2f6;
        position: absolute;
        top: 0;
        left: 0;
    }
    
    /* ==================== END HEADER STYLING ==================== */
    
    /* Adjust main content to not be hidden under fixed header */
    .main {
        background-color: #ffffff !important;
        padding: 0.5rem 1rem !important;
        margin-top: 5rem !important;
    }
    
    .block-container {
        background-color: #ffffff !important;
        padding-top: 1rem !important;
        max-width: 100% !important;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #f0f2f6 !important;
        border-right: 2px solid #d0d5dd;
        margin-top: 0 !important;
        padding-top: 5rem !important;
    }
    
    [data-testid="stSidebar"] > div:first-child {
        background-color: #f0f2f6 !important;
        padding-top: 1rem !important;
        margin-top: 5rem !important;
    }
    
    /* Sidebar collapse button */
    [data-testid="collapsedControl"] {
        top: 5rem !important;
    }
    
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] div {
        color: #000000 !important;
    }
    
    /* Title styling */
    h1, h2, h3, h4, h5, h6 {
        color: #000000 !important;
        font-weight: 600 !important;
    }
    
    h1 {
        font-size: 2rem !important;
        margin-bottom: 1rem !important;
    }
    
    h2 {
        font-size: 1.5rem !important;
        margin-top: 1rem !important;
        margin-bottom: 1rem !important;
    }
    
    h3 {
        font-size: 1.2rem !important;
        margin-top: 1rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    h4 {
        font-size: 1.1rem !important;
        margin-top: 0.8rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* All text black */
    p, span, label, div, li {
        color: #000000 !important;
    }
    
    /* Column borders */
    [data-testid="column"] {
        border: 2px solid #d0d5dd;
        border-radius: 8px;
        padding: 1.5rem;
        background-color: #ffffff !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    /* Metric styling */
    [data-testid="stMetricValue"] {
        color: #000000 !important;
        font-size: 1.5rem !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #000000 !important;
    }
    
    [data-testid="stMetricDelta"] {
        color: #000000 !important;
    }
    
    /* Info boxes */
    .stAlert {
        background-color: #e7f3ff !important;
        border: 1px solid #b3d9ff !important;
        color: #000000 !important;
    }
    
    .stAlert p, .stAlert div {
        color: #000000 !important;
    }
    
    /* Buttons */
    .stButton > button {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 2px solid #d0d5dd !important;
        border-radius: 6px !important;
        font-weight: 500 !important;
    }
    
    .stButton > button:hover {
        background-color: #f0f2f6 !important;
        border-color: #a0a8b8 !important;
    }
    
    /* ==================== SELECTBOX/DROPDOWN STYLING ==================== */
    
    /* Selectbox container */
    [data-testid="stSelectbox"] {
        background-color: #ffffff !important;
    }
    
    /* Selectbox label */
    [data-testid="stSelectbox"] label {
        color: #000000 !important;
        font-weight: 600 !important;
    }
    
    /* Selectbox input */
    [data-testid="stSelectbox"] > div > div {
        background-color: #ffffff !important;
        border: 2px solid #d0d5dd !important;
        border-radius: 6px !important;
    }
    
    /* Selectbox text */
    [data-testid="stSelectbox"] input,
    [data-testid="stSelectbox"] > div > div > div {
        color: #000000 !important;
        background-color: #ffffff !important;
    }
    
    /* Dropdown menu */
    [data-baseweb="popover"] {
        background-color: #ffffff !important;
    }
    
    /* Dropdown options */
    [data-baseweb="menu"] {
        background-color: #ffffff !important;
        border: 2px solid #d0d5dd !important;
    }
    
    [role="option"] {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    
    [role="option"]:hover {
        background-color: #f0f2f6 !important;
        color: #000000 !important;
    }
    
    /* Selected option */
    [aria-selected="true"] {
        background-color: #e7f3ff !important;
        color: #000000 !important;
    }
    
    /* ==================== END SELECTBOX STYLING ==================== */
    
    /* ==================== DATAFRAME STYLING - FORCE BLACK TEXT AND BORDERS ==================== */
    
    /* Main dataframe container */
    [data-testid="stDataFrame"] {
        background-color: #ffffff !important;
    }
    
    [data-testid="stDataFrame"] > div {
        background-color: #ffffff !important;
    }
    
    /* All nested divs in dataframe */
    [data-testid="stDataFrame"] div {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    
    /* Dataframe canvas/container */
    .stDataFrame {
        background-color: #ffffff !important;
    }
    
    /* Table element itself */
    table {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 2px solid #000000 !important;
    }
    
    /* Table headers */
    thead, thead tr, thead th {
        background-color: #f0f2f6 !important;
        color: #000000 !important;
        border: 1px solid #000000 !important;
        font-weight: 600 !important;
    }
    
    /* Table body */
    tbody, tbody tr, tbody td {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #000000 !important;
    }
    
    /* Hover effect */
    tbody tr:hover, tbody tr:hover td {
        background-color: #f8f9fa !important;
        color: #000000 !important;
    }
    
    /* Pandas styler */
    .dataframe {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 2px solid #000000 !important;
    }
    
    .dataframe thead tr th {
        background-color: #f0f2f6 !important;
        color: #000000 !important;
        border: 1px solid #000000 !important;
        font-weight: 600 !important;
    }
    
    .dataframe tbody tr td {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #000000 !important;
    }
    
    /* Streamlit's internal table classes */
    .glideDataEditor {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    
    .dvn-scroller {
        background-color: #ffffff !important;
    }
    
    .dvn-underlay {
        background-color: #ffffff !important;
    }
    
    /* Cell content */
    [data-testid="stDataFrame"] [role="gridcell"] {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #000000 !important;
    }
    
    [data-testid="stDataFrame"] [role="columnheader"] {
        background-color: #f0f2f6 !important;
        color: #000000 !important;
        border: 1px solid #000000 !important;
        font-weight: 600 !important;
    }
    
    /* Force all text in dataframe to be black */
    [data-testid="stDataFrame"] span,
    [data-testid="stDataFrame"] div,
    [data-testid="stDataFrame"] p {
        color: #000000 !important;
    }
    
    /* ==================== END DATAFRAME STYLING ==================== */
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: #f0f2f6 !important;
        color: #000000 !important;
    }
    
    /* Divider */
    hr {
        border-color: #d0d5dd !important;
        margin: 1rem 0 !important;
    }
    
    /* Remove any dark backgrounds */
    div[data-testid="stVerticalBlock"] {
        background-color: #ffffff !important;
    }
    
    section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] {
        background-color: #f0f2f6 !important;
    }
    
    /* Close button styling */
    .close-button {
        background-color: #ff6b6b !important;
        color: #ffffff !important;
        border: none !important;
        padding: 0.5rem 1rem !important;
        border-radius: 6px !important;
        cursor: pointer !important;
        font-weight: 600 !important;
        transition: background-color 0.3s !important;
    }
    
    .close-button:hover {
        background-color: #ff5252 !important;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown('<h2 style="font-size: 1.3rem; margin-top: 0;">⚙️ Settings</h2>', unsafe_allow_html=True)

# Fixed site for now
SITE = "CATALANGA"

# Row 1 - Four columns for maps (2 hàng x 2 cột)
st.markdown('<h2>🗺️ Interactive Coastal Maps</h2>', unsafe_allow_html=True)

# Hàng 1: CoastSat và Microsoft
col1_row1, col2_row1 = st.columns([1, 1], gap="large")

with col1_row1:
    render_column1("CoastSat", SITE)

with col2_row1:
    render_column2("Microsoft", SITE)

st.markdown("<br>", unsafe_allow_html=True)

# Hàng 2: Method 3 và Method 4
col1_row2, col2_row2 = st.columns([1, 1], gap="large")

with col1_row2:
    render_column1_method3("Method3", SITE)

with col2_row2:
    render_column2_method4("Method4", SITE)

st.markdown("---")

# Row 2 - Two columns for analysis WITH DROPDOWN
st.markdown('<h2>📊 Statistical Analysis</h2>', unsafe_allow_html=True)

# Thêm dropdown để chọn phương pháp phân tích
analysis_method = st.selectbox(
    "**Select Analysis Method:**",
    ["Google Earth Engine", "Microsoft Planetary Computer", "Best Curve Fitting", "Method 4", "Other Method"],
    index=0,
    key="analysis_method_selector"
)

st.markdown("---")

col3, col4 = st.columns([1, 1], gap="large")

# Hiển thị columns tương ứng với phương pháp được chọn
if analysis_method == "Google Earth Engine":
    with col3:
        render_column3("CoastSat", SITE)
    with col4:
        render_column4("CoastSat", SITE)

elif analysis_method == "Microsoft Planetary Computer":
    with col3:
        render_column3_microsoft("Microsoft", SITE)
    with col4:
        render_column4_microsoft("Microsoft", SITE)

elif analysis_method == "Best Curve Fitting":  # ✅ SỬA: "Method 3" → "Best Curve Fitting"
    with col3:
        render_column3_method3("Method3", SITE)
    with col4:
        render_column4_method3("Method3", SITE)

elif analysis_method == "Method 4":
    with col3:
        st.info("**Method 4 - Time Series Analysis**\n\nComing soon...")
    with col4:
        st.info("**Method 4 - Summary Statistics**\n\nComing soon...")

elif analysis_method == "Other Method":
    with col3:
        st.info("**Other Method - Column 3**\n\nComing soon...")
    with col4:
        st.info("**Other Method - Column 4**\n\nComing soon...")

st.markdown("---")

# Row 3 - Two columns for Prediction (BỎ DROPDOWN)
st.markdown('<h2>🔮 Prediction</h2>', unsafe_allow_html=True)

col5, col6 = st.columns([1, 1], gap="large")

with col5:
    render_column5("Pre1", SITE)

with col6:
    render_column6("Pre2", SITE)

st.markdown("---")

# Row 4 - Two columns for Planning and Mitigation Options
st.markdown('<h2>🛡️ Planning and Mitigation Options</h2>', unsafe_allow_html=True)

col7, col8 = st.columns([1, 1], gap="large")

with col7:
    render_column7(SITE)

with col8:
    render_column8(SITE)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #6c757d;'>
    <p>Coastal Shoreline Changes Dashboard | Powered by Streamlit & Plotly</p>
</div>
""", unsafe_allow_html=True)