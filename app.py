import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Income Shield Simulator", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# --- 2. THE "EMPIRE" STYLING (MARK XII: READABLE MENUS) ---
st.markdown("""
    <style>
    /* ------------------------------------------------------------------- */
    /* A. MAIN THEME (Dark Navy & White)                                   */
    /* ------------------------------------------------------------------- */
    .stApp {
        background-color: #0E1117;
        color: #FFFFFF;
    }
    [data-testid="stSidebar"] {
        background-color: #161B22;
        border-right: 1px solid #30363d;
    }

    /* ------------------------------------------------------------------- */
    /* B. TEXT & METRICS                                                   */
    /* ------------------------------------------------------------------- */
    h1, h2, h3, h4, h5, h6, p, li, span, div, label {
        color: #FFFFFF !important;
    }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label {
        color: #E6E6E6 !important;
    }
    
    /* Metric Cards */
    div[data-testid="stMetric"] {
        background-color: #1f2937;
        border: 1px solid #374151;
        border-radius: 10px;
        padding: 10px;
    }

    /* ------------------------------------------------------------------- */
    /* C. DROPDOWN MENU FIX (THE CRITICAL PART)                            */
    /* ------------------------------------------------------------------- */
    
    /* 1. The Box you click on */
    div[data-baseweb="select"] > div {
        background-color: #1f2937 !important;
        color: white !important;
        border-color: #374151 !important;
    }
    
    /* 2. The Popup Menu Background */
    ul[data-baseweb="menu"] {
        background-color: #161B22 !important;
    }
    
    /* 3. The Options inside the menu */
    li[role="option"] {
        color: white !important;
    }
    
    /* 4. The Hover Effect (Green) */
    li[role="option"]:hover {
        background-color: #00C805 !important;
        color: black !important; /* Text turns black on green for contrast */
    }
    
    /* 5. The Icons (Down Arrow) */
    .stSelectbox svg {
        fill: white !important;
    }
    
    /* 6. Input Boxes (Number Input) */
    input {
        background-color: #1f2937 !important;
        color: white !important;
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
    st.title("🛡️ Simulator Controls")
    
    tickers = sorted(df_unified['Ticker'].unique())
    selected_ticker = st.selectbox("Select Asset", tickers)
    
    default_date = pd.to_datetime("today") - pd.DateOffset(months=6)
    buy_date = st.date_input("Your Purchase Date", default_date)
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

# --- 5. LOGIC ---
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

fig.add_trace(go.Scatter(
    x=journey['Date'], y=journey['Market_Value'],
    mode='lines', name='Price only (Brokerage View)',
    line=dict(color='#FF4B4B', width=2)
))

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
