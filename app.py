import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Income Shield Simulator",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. THE STYLING (Compact & Jazzed Up) ---
st.markdown("""
    <style>
    /* ------------------------------------------------------------------- */
    /* A. GLOBAL STYLES */
    /* ------------------------------------------------------------------- */
    .stApp {
        background-color: #0D1117;
        color: #E6EDF3;
    }

    /* Kill Scrollbars */
    ::-webkit-scrollbar { display: none !important; }
    
    /* ------------------------------------------------------------------- */
    /* B. COMPONENT STYLING */
    /* ------------------------------------------------------------------- */
    
    /* METRICS: Compact but popped */
    div[data-testid="stMetric"] {
        background-color: #1E293B;
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 10px 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        min-height: 100px; /* Uniform height */
    }
    
    div[data-testid="stMetricLabel"] p { 
        color: #8AC7DE !important; 
        font-size: 0.85rem !important;
        font-weight: 600 !important;
    }
    div[data-testid="stMetricValue"] div { 
        color: #FFFFFF !important; 
        font-size: 1.5rem !important;
        font-weight: 700 !important;
    }

    /* GENERAL TEXT OVERRIDES */
    h1, h2, h3, h4, h5, h6, p, label { color: #E6EDF3 !important; }

    /* INPUTS & DROPDOWNS */
    div[data-baseweb="select"] > div,
    div[data-testid="stDateInput"] > div,
    div[data-baseweb="input"] > div {
        background-color: #1E293B !important;
        border-color: #30363d !important;
        color: #FFFFFF !important;
        font-weight: bold !important;
        border-radius: 6px !important;
        min-height: 40px !important;
    }
    input { color: #FFFFFF !important; font-weight: bold !important; }

    /* DROPDOWN MENUS */
    div[data-baseweb="popover"], div[data-baseweb="menu"], ul[role="listbox"], li[role="option"] {
        background-color: #1E293B !important;
        color: #FFFFFF !important;
        border: 1px solid #30363d !important;
    }
    li[role="option"]:hover, li[role="option"][aria-selected="true"] {
        background-color: #8AC7DE !important;
        color: #0D1117 !important;
    }
    .stSelectbox svg, .stDateInput svg { fill: #8AC7DE !important; }

    /* SIDEBAR COMPACTING */
    .stSidebar .element-container {
        margin-top: 0rem !important;
        margin-bottom: 0.5rem !important;
    }
    .stSidebar .stSelectbox, .stSidebar .stDateInput, .stSidebar .stRadio, .stSidebar .stNumberInput {
        padding-top: 0rem !important;
        padding-bottom: 0rem !important;
    }

    /* ------------------------------------------------------------------- */
    /* C. DESKTOP LAYOUT LOCK (Min-width: 768px) */
    /* ------------------------------------------------------------------- */
    @media (min-width: 768px) {
        
        section[data-testid="stSidebar"] {
            width: 300px !important;
            min-width: 300px !important;
            height: 100vh !important;
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            background-color: #0D1117 !important;
            border-right: 1px solid #30363d !important;
            z-index: 9999 !important;
            transform: none !important;
            padding-top: 1rem !important;
        }
        
        section[data-testid="stSidebar"] h2 {
            padding-top: 0rem !important;
            margin-top: 0rem !important;
            margin-bottom: 1rem !important;
        }

        section[data-testid="stMain"] {
            margin-left: 300px !important;
            width: calc(100% - 300px) !important;
            position: relative !important;
            display: block !important;
        }

        .block-container {
            padding-left: 3rem !important; 
            padding-right: 3rem !important;
            padding-top: 2rem !important;
            padding-bottom: 1rem !important;
            max-width: 100% !important;
        }

        header[data-testid="stHeader"],
        button[data-testid="stSidebarCollapseBtn"],
        div[data-testid="collapsedControl"] {
            display: none !important;
        }
    }

    /* ------------------------------------------------------------------- */
    /* D. MOBILE LAYOUT (Max-width: 767px) */
    /* ------------------------------------------------------------------- */
    @media (max-width: 767px) {
        section[data-testid="stMain"] { margin-left: 0 !important; width: 100% !important; }
        section[data-testid="stSidebar"] { position: relative !important; width: 100% !important; transform: none; }
        .block-container { padding-top: 4rem !important; padding-left: 1rem !important; padding-right: 1rem !important; }
        header[data-testid="stHeader"] { display: block !important; background-color: #0D1117 !important; z-index: 99999 !important; }
        button[data-testid*="SidebarCollapseButton"], [data-testid*="collapsedControl"] { display: block !important; color: #E6EDF3 !important; }
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. DATA LOADING ---
@st.cache_data(ttl=300)
def load_data():
    try:
        u_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSBejJoRecA-lq52GgBYkpqFv7LanUurbzcl4Hqd0QRjufGX-2LSSZjAjPg7DeQ9-Q8o_sc3A9y3739/pub?gid=1848266904&single=true&output=csv"
        h_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSBejJoRecA-lq52GgBYkpqFv7LanUurbzcl4Hqd0QRjufGX-2LSSZjAjPg7DeQ9-Q8o_sc3A9y3739/pub?gid=970184313&single=true&output=csv"
        
        df_u = pd.read_csv(u_url)
        df_h = pd.read_csv(h_url)
        
        df_u['Date'] = pd.to_datetime(df_u['Date'])
        df_h['Date of Pay'] = pd.to_datetime(df_h['Date of Pay'])
        return df_u, df_h
    except Exception as e:
        st.error(f"Data loading error: {str(e)}")
        return None, None

df_unified, df_history = load_data()
if df_unified is None:
    st.stop()

# --- 4. SIDEBAR CONTROLS ---
with st.sidebar:
    st.header("🛡️ Simulator")
    
    tickers = sorted(df_unified['Ticker'].unique())
    selected_ticker = st.selectbox("Select Asset", tickers)
    
    default_date = pd.to_datetime("today") - pd.DateOffset(months=12)
    buy_date = st.date_input("Purchase Date", default_date)
    buy_date = pd.to_datetime(buy_date)
    
    date_mode = st.radio("Simulation End Point:", ["Hold to Present", "Sell on Specific Date"])
    
    if date_mode == "Sell on Specific Date":
        end_date = st.date_input("Sell Date", pd.to_datetime("today"))
        end_date = pd.to_datetime(end_date)
    else:
        end_date = pd.to_datetime("today")
        
    mode = st.radio("Input Method:", ["Share Count", "Dollar Amount"])
    
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
        st.error("No data available for selected date range.")
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

initial_cap = entry_price * shares
current_market_val = journey.iloc[-1]['Market_Value']
cash_total = journey.iloc[-1]['Cash_Banked']
current_total_val = journey.iloc[-1]['True_Value']

market_pl = current_market_val - initial_cap
total_pl = current_total_val - initial_cap
total_return_pct = (total_pl / initial_cap) * 100

start_price = journey.iloc[0]['Closing Price']
end_price_val = journey.iloc[-1]['Closing Price']
price_line_color = '#8AC7DE' if end_price_val >= start_price else '#FF4B4B'

# --- NEW: ANNUALIZED YIELD CALCULATION ---
days_held = (end_date - buy_date).days
if days_held > 0:
    # (Dividends / Initial) * (365 / Days)
    raw_yield = cash_total / initial_cap
    annual_yield = raw_yield * (365.25 / days_held) * 100
else:
    annual_yield = 0.0

# --- 6. DASHBOARD ---
try:
    meta_row = price_df.iloc[0]
    asset_underlying = meta_row.get('Underlying', '-')
    asset_company = meta_row.get('Company', '-')
except Exception:
    asset_underlying = "-"
    asset_company = "-"

# --- HEADER SECTION (Performance Added Back) ---
col_head, col_meta = st.columns([2.5, 1])

with col_head:
    st.markdown(f"""
        <div style="margin-top: -10px;">
            <h1 style="font-size: 2.5rem; margin-bottom: 0px; color: #E6EDF3; line-height: 1.2;">
                {selected_ticker} <span style="color: #8AC7DE;">Performance Simulator</span>
            </h1>
            <p style="font-size: 1.1rem; color: #8AC7DE; opacity: 0.8; margin-top: -5px; margin-bottom: 10px;">
                <b>{shares:.2f} shares</b> &nbsp;|&nbsp; {buy_date.date()} ➝ {end_date.date()} ({days_held} days)
            </p>
        </div>
    """, unsafe_allow_html=True)

with col_meta:
    st.markdown(f"""
        <div style="display: flex; gap: 8px; justify-content: flex-end; align-items: center; height: 100%; padding-top: 5px;">
            <div style="background: rgba(30, 41, 59, 0.7); border: 1px solid #30363d; border-radius: 8px; padding: 8px 12px; text-align: center; min-width: 90px;">
                <div style="color: #8AC7DE; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1px;">Underlying</div>
                <div style="color: white; font-size: 1.1rem; font-weight: 800;">{asset_underlying}</div>
            </div>
            <div style="background: rgba(30, 41, 59, 0.7); border: 1px solid #30363d; border-radius: 8px; padding: 8px 12px; text-align: center; min-width: 90px;">
                <div style="color: #8AC7DE; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1px;">Company</div>
                <div style="color: white; font-size: 1.1rem; font-weight: 800;">{asset_company}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# --- 5 COLUMNS ---
m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Initial Capital", f"${initial_cap:,.2f}")
m2.metric("Market Value", f"${current_market_val:,.2f}", f"{market_pl:,.2f}")
m3.metric("Dividends Collected", f"${cash_total:,.2f}", f"+{cash_total:,.2f}")
m4.metric("Annualized Yield", f"{annual_yield:.2f}%", help="Div Yield normalized to 1 year (Average if >1yr, Extrapolated if <1yr)")
m5.metric("True Total Value", f"${current_total_val:,.2f}", f"{total_return_pct:.2f}%")

# --- 7. CHART ---
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=journey['Date'], y=journey['Market_Value'],
    mode='lines', name='Price only',
    line=dict(color=price_line_color, width=2)
))

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
    height=380,
    margin=dict(l=0, r=0, t=30, b=0),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1,
        font=dict(color="#E6EDF3")
    ),
    hovermode="x unified",
    xaxis = dict(
        fixedrange = True
    ),
    yaxis = dict(
        fixedrange = True
    )
)

st.plotly_chart(fig, use_container_width=True, config={
    'displayModeBar': False,
    'staticPlot': False
})

# Data breakdown
with st.expander("View Data"):
    st.dataframe(
        journey[['Date', 'Closing Price', 'Market_Value', 'Cash_Banked', 'True_Value']]
            .sort_values('Date', ascending=False),
        use_container_width=True,
        height=200
    )
