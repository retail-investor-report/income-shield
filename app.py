import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Income Shield Simulator", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# --- 2. THE "EMPIRE" STYLING (MARK XV: PAINT IT BLACK) ---
# Core: #0D1117 | Accent: #8AC7DE | Tertiary: #1E293B
st.markdown("""
    <style>
    /* ------------------------------------------------------------------- */
    /* A. GLOBAL LAYOUT & COLORS                                           */
    /* ------------------------------------------------------------------- */
    .stApp {
        background-color: #0D1117; 
        color: #E6EDF3;
    }
    [data-testid="stSidebar"] {
        background-color: #0D1117; 
        border-right: 1px solid #30363d;
    }

    /* ------------------------------------------------------------------- */
    /* B. THE HEADER & ARROW FIX (THE CRITICAL CHANGE)                     */
    /* ------------------------------------------------------------------- */
    
    /* 1. We do NOT hide the header. We paint it #0D1117 */
    header[data-testid="stHeader"] {
        background-color: #0D1117 !important;
        height: 3.5rem !important; /* Fixed height to prevent shifting */
        z-index: 100 !important;
    }
    
    /* 2. We Hide the Toolbar buttons (Deploy, etc.) individually */
    [data-testid="stToolbar"] {
        display: none !important;
    }
    
    /* 3. We Hide the Rainbow Decoration Line */
    [data-testid="stDecoration"] {
        display: none !important;
    }

    /* 4. We Style the Arrow Button (Which sits inside the now-black header) */
    [data-testid="stSidebarCollapsedControl"] {
        color: #8AC7DE !important; /* Accent Blue */
        display: block !important;
    }
    
    /* 5. The Close "X" Button */
    [data-testid="stSidebarCollapseBtn"] {
        color: #8AC7DE !important;
    }

    /* ------------------------------------------------------------------- */
    /* C. DROPDOWN & INPUT VISIBILITY (NUCLEAR OVERRIDE)                   */
    /* ------------------------------------------------------------------- */
    
    /* The Box you click */
    div[data-baseweb="select"] > div, 
    div[data-testid="stDateInput"] > div,
    div[data-baseweb="input"] > div {
        background-color: #1E293B !important; /* Tertiary Navy */
        border-color: #30363d !important;
        color: #FFFFFF !important;
    }
    
    /* The Text inside */
    input {
        color: #FFFFFF !important;
    }
    
    /* The Popup Menu Container */
    div[data-baseweb="popover"] {
        background-color: #1E293B !important;
    }
    
    /* The Menu List */
    ul[data-baseweb="menu"] {
        background-color: #1E293B !important;
    }
    
    /* The Options */
    li[role="option"] {
        color: #FFFFFF !important;
    }
    
    /* Hover Highlight */
    li[role="option"]:hover, li[role="option"]:focus {
        background-color: #8AC7DE !important;
        color: #0D1117 !important;
    }
    
    /* Icons */
    .stSelectbox svg, .stDateInput svg {
        fill: #8AC7DE !important;
    }

    /* ------------------------------------------------------------------- */
    /* D. ANTI-SCROLL & COMPACTNESS                                        */
    /* ------------------------------------------------------------------- */
    
    /* Remove huge top padding so it fits in one window */
    .block-container {
        padding-top: 1.5rem !important; 
        padding-bottom: 0rem !important;
        max-width: 100%;
    }
    
    /* Hide Footer */
    footer {
        display: none !important;
    }

    /* ------------------------------------------------------------------- */
    /* E. METRICS & TEXT                                                   */
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
    st.title("🛡️ Simulator")
    
    # Ticker
    tickers = sorted(df_unified['Ticker'].unique())
    selected_ticker = st.selectbox("Select Asset", tickers)
    
    st.markdown("---")
    
    # 1. Start Date
    default_date = pd.to_datetime("today") - pd.DateOffset(months=12)
    buy_date = st.date_input("Purchase Date", default_date)
    buy_date = pd.to_datetime(buy_date)
    
    # 2. End Date Logic (The Requested Feature)
    st.write("Duration:")
    is_custom_end = st.checkbox("Simulate to Specific Date")
    
    if is_custom_end:
        end_date = st.date_input("End Date", pd.to_datetime("today"))
        end_date = pd.to_datetime(end_date)
    else:
        st.caption("✅ Simulating returns to Present Day")
        end_date = pd.to_datetime("today")
        
    st.markdown("---")
    
    # 3. Position Size
    mode = st.radio("Input Method:", ["Share Count", "Dollar Amount"])
    
    # 4. Data Filtering Logic
    price_df = df_unified[df_unified['Ticker'] == selected_ticker].sort_values('Date')
    
    # Filter between Buy Date AND End Date
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
        st.error("No data available for this date range.")
        st.stop()

# --- 5. CALCULATIONS ---
div_df = df_history[df_history['Ticker'] == selected_ticker].sort_values('Date of Pay')
# Filter dividends to only those paid within the hold period
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
# Blue (#8AC7DE) if up, Red (#FF4B4B) if down
price_line_color = '#8AC7DE' if end_price_val >= start_price else '#FF4B4B'

# --- 6. DASHBOARD ---
st.header(f"{selected_ticker} Performance Simulator")
date_range_str = f"{buy_date.date()} ➝ {end_date.date()}"
st.markdown(f"**{shares:.2f} shares** | {date_range_str}")

m1, m2, m3, m4 = st.columns(4)

m1.metric("Initial Capital", f"${initial_cap:,.2f}")
m2.metric("Market Value", f"${current_market_val:,.2f}", f"{market_pl:,.2f}")
m3.metric("Dividends Collected", f"${cash_total:,.2f}", f"+{cash_total:,.2f}")
m4.metric("True Total Value", f"${current_total_val:,.2f}", f"{total_return_pct:.2f}%")

# --- 7. CHART ---
fig = go.Figure()

# Price Line (Dynamic Color)
fig.add_trace(go.Scatter(
    x=journey['Date'], y=journey['Market_Value'],
    mode='lines', name='Price only (Brokerage View)',
    line=dict(color=price_line_color, width=2)
))

# True Value Line (Always Neon Green)
fig.add_trace(go.Scatter(
    x=journey['Date'], y=journey['True_Value'],
    mode='lines', name='True Value (Price + Dividends)',
    line=dict(color='#00C805', width=3),
    fill='tonexty', 
    fillcolor='rgba(0, 200, 5, 0.1)' 
))

fig.add_hline(y=initial_cap, line_dash="dash", line_color="white", opacity=0.3)

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

with st.expander("View Raw Data Table"):
    st.dataframe(journey[['Date', 'Closing Price', 'Market_Value', 'Cash_Banked', 'True_Value']].sort_values('Date', ascending=False), use_container_width=True)
