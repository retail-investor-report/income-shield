import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Income Shield Simulator", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# --- 2. THE "BRAND" STYLING (MARK XIII) ---
# We are manually injecting your specific color palette.
# Core: #0D1117 | Accent: #8AC7DE | Tertiary: #1E293B
st.markdown("""
    <style>
    /* ------------------------------------------------------------------- */
    /* A. CORE BACKGROUNDS                                                 */
    /* ------------------------------------------------------------------- */
    
    /* The Main App Background */
    .stApp {
        background-color: #0D1117; /* Core */
        color: #E6EDF3; /* Primary Text */
    }
    
    /* The Sidebar Background */
    [data-testid="stSidebar"] {
        background-color: #0D1117; /* Core (Match main for seamless look) */
        border-right: 1px solid #30363d;
    }
    
    /* THE HEADER FIX: Force it to be Dark so the arrow is visible */
    header[data-testid="stHeader"] {
        background-color: #0D1117 !important;
    }

    /* ------------------------------------------------------------------- */
    /* B. INPUTS & DROPDOWNS (The Visibility Fix)                          */
    /* ------------------------------------------------------------------- */
    
    /* 1. The Input Box Container (Dropdowns, Date Pickers, Number Inputs) */
    div[data-baseweb="select"] > div, 
    div[data-baseweb="input"] > div,
    div[data-testid="stDateInput"] > div {
        background-color: #1E293B !important; /* Tertiary */
        color: #FFFFFF !important;
        border-color: #30363d !important;
    }
    
    /* 2. The Text INSIDE the Input Box */
    input {
        color: #FFFFFF !important;
    }
    
    /* 3. The Popup Menu (The list that opens up) */
    ul[data-baseweb="menu"] {
        background-color: #1E293B !important; /* Tertiary */
    }
    
    /* 4. The Options inside the menu */
    li[role="option"] {
        color: #FFFFFF !important; /* Secondary */
    }
    
    /* 5. Hover Effect for Options */
    li[role="option"]:hover {
        background-color: #8AC7DE !important; /* Accent Blue */
        color: #0D1117 !important; /* Dark text on blue bg */
    }
    
    /* 6. The Down Arrow / Calendar Icons */
    .stSelectbox svg, .stDateInput svg {
        fill: #8AC7DE !important; /* Accent Blue */
    }
    
    /* ------------------------------------------------------------------- */
    /* C. TEXT & METRICS                                                   */
    /* ------------------------------------------------------------------- */
    
    /* Global Text Override */
    h1, h2, h3, h4, h5, h6, p, li, span, div, label {
        color: #E6EDF3 !important; /* Primary Text */
    }
    
    /* Metric Cards */
    div[data-testid="stMetric"] {
        background-color: #1E293B; /* Tertiary */
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 10px;
    }
    
    /* Metric Labels (Top small text) */
    div[data-testid="stMetricLabel"] p {
        color: #8AC7DE !important; /* Accent Blue */
    }
    
    /* Metric Values (Big numbers) */
    div[data-testid="stMetricValue"] div {
        color: #FFFFFF !important; /* Secondary White */
    }

    /* ------------------------------------------------------------------- */
    /* D. NAVIGATION & ARROWS                                              */
    /* ------------------------------------------------------------------- */
    
    /* The Sidebar Toggle Arrow (Top Left) */
    [data-testid="stSidebarCollapsedControl"] {
        color: #8AC7DE !important; /* Accent Blue */
        background-color: transparent !important;
    }
    
    /* The Sidebar Close Button (X) */
    [data-testid="stSidebarCollapseBtn"] {
        color: #8AC7DE !important;
    }
    
    /* Hide unwanted Toolbar buttons */
    [data-testid="stToolbar"] {
        visibility: hidden !important;
    }
    
    /* Hide Decoration Bar */
    [data-testid="stDecoration"] {
        display: none !important;
    }
    
    /* Clean up top spacing */
    .block-container {
        padding-top: 2rem !important; 
        max-width: 100%;
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

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("🛡️ Simulator")
    
    tickers = sorted(df_unified['Ticker'].unique())
    selected_ticker = st.selectbox("Select Asset", tickers)
    
    default_date = pd.to_datetime("today") - pd.DateOffset(months=6)
    buy_date = st.date_input("Purchase Date", default_date)
    buy_date = pd.to_datetime(buy_date)

    st.markdown("---")
    
    mode = st.radio("Input Method:", ["Share Count", "Dollar Amount"])
    
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

# --- 5. LOGIC & CALCULATIONS ---
div_df = df_history[df_history['Ticker'] == selected_ticker].sort_values('Date of Pay')
my_divs = div_df[div_df['Date of Pay'] >= buy_date].copy()
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

# Chart Logic: Determine Price Line Color
start_price = journey.iloc[0]['Closing Price']
end_price = journey.iloc[-1]['Closing Price']
# Blue (#8AC7DE) if up, Red (#FF4B4B) if down
price_line_color = '#8AC7DE' if end_price >= start_price else '#FF4B4B'

# --- 6. DASHBOARD ---
st.header(f"{selected_ticker} Performance Simulator")
st.markdown(f"Analysis for **{shares:.2f} shares** purchased on **{buy_date.date()}**.")

m1, m2, m3, m4 = st.columns(4)

m1.metric("Initial Capital", f"${initial_cap:,.2f}")
m2.metric("Market Value", f"${current_market_val:,.2f}", f"{market_pl:,.2f}")
m3.metric("Dividends Collected", f"${cash_total:,.2f}", f"+{cash_total:,.2f}")
m4.metric("True Total Value", f"${current_total_val:,.2f}", f"{total_return_pct:.2f}%")

# --- 7. CHART ---
fig = go.Figure()

# Price Line (Dynamic Color: Blue/Red)
fig.add_trace(go.Scatter(
    x=journey['Date'], y=journey['Market_Value'],
    mode='lines', name='Price only (Brokerage View)',
    line=dict(color=price_line_color, width=2)
))

# True Value Line (Always Neon Green for Income Shield)
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
