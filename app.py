import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Income Shield Simulator", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# --- 2. THE "EMPIRE" STYLING (FINAL: ARROW RESCUE) ---
st.markdown("""
    <style>
    /* 1. MAIN LAYOUT & BACKGROUND */
    .stApp {
        background-color: #0E1117;
        color: #FFFFFF;
    }
    
   # --- 2. THE "EMPIRE" STYLING (FINAL: GHOST MODE HEADER) ---
st.markdown("""
    <style>
    /* 1. MAIN LAYOUT & BACKGROUND */
    .stApp {
        background-color: #0E1117;
        color: #FFFFFF;
    }
    
    /* 2. REMOVE THE 'PHANTOM' SCROLLING & PADDING */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 0rem !important;
        max-width: 100%;
    }
    
    /* 3. GLOBAL TEXT OVERRIDES */
    h1, h2, h3, h4, h5, h6, p, span, div {
        color: #FFFFFF !important;
    }

    /* 4. SIDEBAR STYLING */
    [data-testid="stSidebar"] {
        background-color: #161B22;
        border-right: 1px solid #30363d;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] p, [data-testid="stSidebar"] label {
        color: #E6E6E6 !important;
    }

    /* 5. METRIC CARD STYLING */
    div[data-testid="stMetric"] {
        background-color: #1f2937;
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #374151;
        text-align: center;
    }
    div[data-testid="stMetricLabel"] p {
        color: #9CA3AF !important; 
    }
    div[data-testid="stMetricValue"] div {
        color: #00C805 !important; 
    }
    
    /* 6. "GHOST MODE" HEADER (The Fix) */
    
    /* We do NOT hide the header. We make it transparent. */
    header {
        background-color: transparent !important; 
    }
    
    /* We HIDE the specific Toolbar (Deploy, hamburger, etc.) */
    [data-testid="stToolbar"] {
        display: none !important; 
    }
    
    /* We HIDE the colorful decoration bar at the top */
    [data-testid="stDecoration"] {
        display: none !important;
    }
    
    /* We HIDE the footer */
    footer {
        visibility: hidden !important;
    }
    
    /* 7. ARROW STYLING (Now perfectly safe) */
    [data-testid="stSidebarCollapsedControl"] {
        color: #00C805 !important; /* Green Arrow */
    }
    
    [data-testid="stSidebarCollapseBtn"] {
        color: #00C805 !important;
    }

    /* 8. SCROLLBAR HIDING */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #0E1117; 
    }
    ::-webkit-scrollbar-thumb {
        background: #30363d; 
        border-radius: 4px;
    }

    /* 9. FORM ELEMENT FIXES (Dropdowns) */
    div[data-baseweb="select"] > div {
        background-color: #1f2937 !important;
        color: white !important;
        border-color: #374151 !important;
    }
    ul[data-baseweb="menu"] {
        background-color: #161B22 !important; 
    }
    li[role="option"] {
        color: white !important; 
    }
    li[role="option"]:hover {
        background-color: #00C805 !important; 
        color: black !important;
    }
    .stSelectbox svg {
        fill: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. THE LIVE WIRE: DATA LOADING ---
@st.cache_data(ttl=300)
def load_data():
    try:
        # ---------------------------------------------------------
        # PASTE YOUR GOOGLE SHEET LINKS BETWEEN THE QUOTES BELOW
        # ---------------------------------------------------------
        u_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSBejJoRecA-lq52GgBYkpqFv7LanUurbzcl4Hqd0QRjufGX-2LSSZjAjPg7DeQ9-Q8o_sc3A9y3739/pub?gid=728728946&single=true&output=csv"
        h_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSBejJoRecA-lq52GgBYkpqFv7LanUurbzcl4Hqd0QRjufGX-2LSSZjAjPg7DeQ9-Q8o_sc3A9y3739/pub?gid=970184313&single=true&output=csv"
        
        df_u = pd.read_csv(u_url)
        df_h = pd.read_csv(h_url)
        
        # Convert Dates
        df_u['Date'] = pd.to_datetime(df_u['Date'])
        df_h['Date of Pay'] = pd.to_datetime(df_h['Date of Pay'])
        return df_u, df_h
    except Exception as e:
        return None, None

df_unified, df_history = load_data()

if df_unified is None:
    st.error("🚨 Link Connection Error: Check your Google Sheet CSV links in the code.")
    st.stop()

# --- 4. SIDEBAR CONTROLS ---
with st.sidebar:
    st.title("🛡️ Simulator Controls")
    st.write("Adjust your entry and position size.")
    
    # Ticker Selection
    tickers = sorted(df_unified['Ticker'].unique())
    selected_ticker = st.selectbox("Select Asset", tickers)
    
    # Buy Date (Default to 6 months ago)
    default_date = pd.to_datetime("today") - pd.DateOffset(months=6)
    buy_date = st.date_input("Your Purchase Date", default_date)
    buy_date = pd.to_datetime(buy_date)

    st.markdown("---")
    
    # Mode Selection
    mode = st.radio("Input Method:", ["Share Count", "Dollar Amount"])
    
    # Filter data for calculations
    price_df = df_unified[df_unified['Ticker'] == selected_ticker].sort_values('Date')
    journey = price_df[price_df['Date'] >= buy_date].copy()
    
    if not journey.empty:
        entry_price = journey.iloc[0]['Closing Price']
        if mode == "Share Count":
            shares = st.number_input("Shares Owned", min_value=1, value=10)
        else:
            dollars = st.number_input("Amount Invested ($)", min_value=100, value=1000, step=100)
            shares = float(dollars) / entry_price
        
        st.info(f"Entry Price: ${entry_price:.2f}")
    else:
        st.error("No data available for this date.")
        st.stop()

# --- 5. CALCULATIONS ---
# Dividend processing
div_df = df_history[df_history['Ticker'] == selected_ticker].sort_values('Date of Pay')
my_divs = div_df[div_df['Date of Pay'] >= buy_date].copy()
my_divs['CumDiv'] = my_divs['Amount'].cumsum()

def get_total_div(d):
    rows = my_divs[my_divs['Date of Pay'] <= d]
    return rows['CumDiv'].iloc[-1] if not rows.empty else 0.0

# Build the timeline
journey['Div_Per_Share'] = journey['Date'].apply(get_total_div)
journey['Market_Value'] = journey['Closing Price'] * shares
journey['Cash_Banked'] = journey['Div_Per_Share'] * shares
journey['True_Value'] = journey['Market_Value'] + journey['Cash_Banked']

# Final Stats
initial_cap = entry_price * shares
current_total = journey.iloc[-1]['True_Value']
cash_total = journey.iloc[-1]['Cash_Banked']
total_return_pct = ((current_total - initial_cap) / initial_cap) * 100

# --- 6. MAIN DASHBOARD ---
st.header(f" {selected_ticker} Performance Simulator")
st.markdown(f"Analysis for **{shares:.2f} shares** purchased on **{buy_date.date()}**.")

# Metric Row
m1, m2, m3, m4 = st.columns(4)
m1.metric("Initial Capital", f"${initial_cap:,.2f}")
m2.metric("Market Value", f"${journey.iloc[-1]['Market_Value']:,.2f}")
m3.metric("Dividends Collected", f"${cash_total:,.2f}")
m4.metric("True Total Value", f"${current_total:,.2f}", f"{total_return_pct:.2f}%")

# --- 7. THE CHART ---
fig = go.Figure()

# Market Price (Red Line)
fig.add_trace(go.Scatter(
    x=journey['Date'], y=journey['Market_Value'],
    mode='lines', name='Price only (Brokerage View)',
    line=dict(color='#FF4B4B', width=1.5)
))

# Total Return (Green Line + Shading)
fig.add_trace(go.Scatter(
    x=journey['Date'], y=journey['True_Value'],
    mode='lines', name='True Value (Price + Dividends)',
    line=dict(color='#00C805', width=3),
    fill='tonexty', 
    fillcolor='rgba(0, 200, 5, 0.15)' 
))

# Break-even Reference
fig.add_hline(y=initial_cap, line_dash="dash", line_color="#888888", opacity=0.5)

fig.update_layout(
    template="plotly_dark",
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    height=500,
    margin=dict(l=0, r=0, t=20, b=0),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    hovermode="x unified"
)

st.plotly_chart(fig, use_container_width=True)

# Data breakdown
with st.expander("View Raw Data Table"):
    st.dataframe(journey[['Date', 'Closing Price', 'Market_Value', 'Cash_Banked', 'True_Value']].sort_values('Date', ascending=False), use_container_width=True)





