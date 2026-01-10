import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Income Shield Simulator",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. THE "EMPIRE" STYLING (MARK XVII: THE MONOLITH) ---
# Core: #0D1117 | Accent: #8AC7DE | Tertiary: #1E293B
st.markdown("""
    <style>
    /* ------------------------------------------------------------------- */
    /* A. GLOBAL LAYOUT & COLORS */
    /* ------------------------------------------------------------------- */
    .stApp {
        background-color: #0D1117;
        color: #E6EDF3;
    }
   
    /* ------------------------------------------------------------------- */
    /* B. PERMANENT SIDEBAR (LOCKED OPEN) */
    /* ------------------------------------------------------------------- */
   
    [data-testid="stSidebar"] {
        background-color: #0D1117;
        border-right: 1px solid #30363d;
        width: 300px !important; /* Fixed width */
        min-width: 300px !important; /* Prevent collapse */
        max-width: 300px !important;
        transform: translateX(0) !important; /* Force visible position */
        left: 0 !important;
        display: flex !important; /* Ensure layout */
        visibility: visible !important;
        transition: none !important; /* Disable slide animation */
        overflow-y: hidden !important; /* Prevent scrolling */
    }
    /* Hide collapse button (expanded state) */
    button[data-testid="stSidebarCollapseButton"],
    button[kind="collapseSidebar"] {
        display: none !important;
    }
   
    /* Hide expand arrow (collapsed state) */
    div[data-testid="collapsedControl"],
    [data-testid="collapsedControl"] {
        display: none !important;
    }
   
    /* Prevent any collapse behavior */
    [data-testid="stSidebarNav"] {
        pointer-events: none !important;
    }
   
    /* Compact sidebar content */
    section[data-testid="stSidebar"] > div > div > div > div.block-container {
        padding-top: 0.5rem !important;
        padding-bottom: 0.5rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
   
    /* Reduce margins between elements in sidebar */
    .stSidebar .element-container,
    .stSidebar .stSelectbox,
    .stSidebar .stDateInput,
    .stSidebar .stRadio,
    .stSidebar .stNumberInput,
    .stSidebar .stMarkdown,
    .stSidebar .stInfo {
        margin-top: 0.5rem !important;
        margin-bottom: 0.5rem !important;
    }
   
    /* Make horizontal rules thinner */
    .stSidebar hr {
        margin: 0.5rem 0 !important;
        border-top: 1px solid #30363d !important;
    }
   
    /* ------------------------------------------------------------------- */
    /* C. HEADER FIX (NO WHITE BANNER) */
    /* ------------------------------------------------------------------- */
   
    /* Completely hide the header bar */
    header[data-testid="stHeader"] {
        display: none !important;
    }
   
    /* Hide Toolbar & Decoration */
    [data-testid="stToolbar"] {display: none !important;}
    [data-testid="stDecoration"] {display: none !important;}
    footer {display: none !important;}
   
    /* Adjust main content to start from top */
    .main {
        padding-top: 0 !important;
    }
   
    /* ------------------------------------------------------------------- */
    /* D. DROPDOWN VISIBILITY (HIGH CONTRAST) */
    /* ------------------------------------------------------------------- */
   
    /* The Box you click */
    div[data-baseweb="select"] > div,
    div[data-testid="stDateInput"] > div,
    div[data-baseweb="input"] > div {
        background-color: #1E293B !important;
        border-color: #30363d !important;
        color: #FFFFFF !important;
        font-weight: bold !important; /* Bolder text for better visibility */
    }
   
    /* The Text inside input boxes */
    input {
        color: #FFFFFF !important;
        font-weight: bold !important;
    }
   
    /* THE POPUP MENU (Dark Background, White Text) - Higher specificity */
    div[data-baseweb="popover"],
    div[data-baseweb="menu"] {
        background-color: #1E293B !important;
        border: 1px solid #30363d !important;
    }
   
    /* Nested menu structure for override */
    div[data-baseweb="popover"] > div[data-baseweb="menu"] {
        background-color: #1E293B !important;
        border: 1px solid #30363d !important;
    }
   
    div[data-baseweb="menu"] > ul[role="listbox"] {
        background-color: #1E293B !important;
        border: none !important;
    }
   
    /* The List Items */
    ul[role="listbox"] > li[role="option"] {
        background-color: #1E293B !important;
        color: #FFFFFF !important;
        font-weight: bold !important; /* Bolder text */
        padding: 12px !important; /* More padding for readability */
    }
   
    /* Hover Highlight (Blue Background, Dark Text) */
    ul[role="listbox"] > li[role="option"]:hover,
    ul[role="listbox"] > li[role="option"][aria-selected="true"] {
        background-color: #8AC7DE !important;
        color: #0D1117 !important;
    }
   
    /* Icons */
    .stSelectbox svg, .stDateInput svg {
        fill: #8AC7DE !important;
    }
    /* ------------------------------------------------------------------- */
    /* E. RADIO BUTTONS (REVERTED TO CIRCLES) */
    /* ------------------------------------------------------------------- */
    div[role="radiogroup"] label {
        color: #E6EDF3 !important;
    }
    /* ------------------------------------------------------------------- */
    /* F. ANTI-SCROLL (COMPACT LAYOUT) */
    /* ------------------------------------------------------------------- */
   
    /* Push content up to the very top */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 0rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        max-width: 100%;
    }
   
    /* Hide Scrollbars */
    ::-webkit-scrollbar {
        display: none;
    }
   
    /* ------------------------------------------------------------------- */
    /* G. METRICS & TEXT */
    /* ------------------------------------------------------------------- */
    h1, h2, h3, h4, h5, h6, p, label {
        color: #E6EDF3 !important;
    }
   
    div[data-testid="stMetric"] {
        background-color: #1E293B;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 10px;
    }
    div[data-testid="stMetricLabel"] p {
        color: #8AC7DE !important;
    }
    div[data-testid="stMetricValue"] div {
        color: #FFFFFF !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATA LOADING ---
@st.cache_data(ttl=300)
def load_data():
    try:
        u_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSBejJoRecA-lq52GgBYkpqFv7LanUurbzcl4Hqd0QRjufGX-2LSSZjAjPg7DeQ9-Q8o_sc3A9y3739/pub?gid=728728946&single=true&output=csv"
        h_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSBejJoRecA-lq52GgBYkpqFv7LanUurbzcl4Hqd0QRjufGX-2LSSZjAjPg7DeQ9-Q8o_sc3A9y3739/pub?gid=970184313&single=true&output=csv"
       
        df_u = pd.read_csv(u_url)
        df_h = pd.read_csv(h_url)
       
        df_u['Date'] = pd.to_datetime(df_u['Date'])
        df_h['Date of Pay'] = pd.to_datetime(df_h['Date of Pay'])
        return df_u, df_h
    except Exception as e:
        return None, None

df_unified, df_history = load_data()
if df_unified is None:
    st.error("🚨 Link Connection Error: Check your Google Sheet CSV links.")
    st.stop()

# --- 4. SIDEBAR CONTROLS ---
with st.sidebar:
    st.header("🛡️ Simulator")
   
    # Ticker
    tickers = sorted(df_unified['Ticker'].unique())
    selected_ticker = st.selectbox("Select Asset", tickers)
   
    st.markdown("---")
   
    # 1. Start Date
    default_date = pd.to_datetime("today") - pd.DateOffset(months=12)
    buy_date = st.date_input("Purchase Date", default_date)
    buy_date = pd.to_datetime(buy_date)
   
    # 2. End Date Logic (Reverted to Radio Buttons as requested)
    date_mode = st.radio("Simulation End Point:", ["Hold to Present", "Sell on Specific Date"])
   
    if date_mode == "Sell on Specific Date":
        end_date = st.date_input("Sell Date", pd.to_datetime("today"))
        end_date = pd.to_datetime(end_date)
    else:
        end_date = pd.to_datetime("today")
       
    st.markdown("---")
   
    # 3. Position Size
    mode = st.radio("Input Method:", ["Share Count", "Dollar Amount"])
   
    # 4. Data Filtering Logic
    price_df = df_unified[df_unified['Ticker'] == selected_ticker].sort_values('Date')
    journey = price_df[(price_df['Date'] >= buy_date) & (price_df['Date'] <= end_date)].copy()
   
    if not journey.empty:
        entry_price = journey.iloc[0]['Closing Price']
        if mode == "Share Count":
            shares = st.number_input("Shares Owned", min_value=1, value=10)
        else:
            dollars = st.number_input("Amount Invested ($)", min_value=100, value=1000, step=100)
            shares = float(dollars) / entry_price
       
        st.info(f"Entry Price: ${entry_price:.2f}")
    else:
        st.error("No data available.")
        st.stop()

# --- 5. CALCULATIONS ---
div_df = df_history[df_history['Ticker'] == selected_ticker].sort_values('Date of Pay')
my_divs = div_df[(div_df['Date of Pay'] >= buy_date) & (div_df['Date of Pay'] <= end_date)].copy()
my_divs['CumDiv'] = my_divs['Amount'].cumsum()

def get_total_div(d):
    rows = my_divs[my_divs['Date of Pay'] <= d]
    return rows['CumDiv'].iloc[-1] if not rows.empty else 0.0

journey['Div_Per_Share'] = journey['Date'].apply(get_total_div)
journey['Market_Value'] = journey['Closing Price'] * shares
journey['Cash_Banked'] = journey['Div_Per_Share'] * shares
journey['True_Value'] = journey['Market_Value'] + journey['Cash_Banked']

# Totals
initial_cap = entry_price * shares
current_market_val = journey.iloc[-1]['Market_Value']
cash_total = journey.iloc[-1]['Cash_Banked']
current_total_val = journey.iloc[-1]['True_Value']

# Deltas
market_pl = current_market_val - initial_cap
total_pl = current_total_val - initial_cap
total_return_pct = (total_pl / initial_cap) * 100

# Chart Color Logic
start_price = journey.iloc[0]['Closing Price']
end_price_val = journey.iloc[-1]['Closing Price']
price_line_color = '#8AC7DE' if end_price_val >= start_price else '#FF4B4B'

# --- 6. DASHBOARD ---
# Compact Header
st.markdown(f"### {selected_ticker} Performance Simulator")
st.markdown(f"**{shares:.2f} shares** | {buy_date.date()} ➝ {end_date.date()}")

m1, m2, m3, m4 = st.columns(4)
m1.metric("Initial Capital", f"${initial_cap:,.2f}")
m2.metric("Market Value", f"${current_market_val:,.2f}", f"{market_pl:,.2f}")
m3.metric("Dividends Collected", f"${cash_total:,.2f}", f"+{cash_total:,.2f}")
m4.metric("True Total Value", f"${current_total_val:,.2f}", f"{total_return_pct:.2f}%")

# --- 7. CHART ---
fig = go.Figure()
# Price Line
fig.add_trace(go.Scatter(
    x=journey['Date'], y=journey['Market_Value'],
    mode='lines', name='Price only',
    line=dict(color=price_line_color, width=2)
))
# True Value Line
fig.add_trace(go.Scatter(
    x=journey['Date'], y=journey['True_Value'],
    mode='lines', name='True Value (Price + Divs)',
    line=dict(color='#00C805', width=3),
    fill='tonexty',
    fillcolor='rgba(0, 200, 5, 0.1)'
))
fig.add_hline(y=initial_cap, line_dash="dash", line_color="white", opacity=0.3)
fig.update_layout(
    template="plotly_dark",
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    height=380, # Compact Height
    margin=dict(l=0, r=0, t=20, b=0),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    hovermode="x unified"
)
st.plotly_chart(fig, use_container_width=True)

# Data breakdown (Compact)
with st.expander("View Data"):
    st.dataframe(journey[['Date', 'Closing Price', 'Market_Value', 'Cash_Banked', 'True_Value']].sort_values('Date', ascending=False), use_container_width=True, height=200)
