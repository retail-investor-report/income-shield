import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Income Shield Simulator",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. THE "EMPIRE" STYLING (LOCKED DESKTOP / NATIVE MOBILE) ---
st.markdown("""
    <style>
    /* ------------------------------------------------------------------- */
    /* A. GLOBAL COLORS (Applies everywhere) */
    /* ------------------------------------------------------------------- */
    .stApp {
        background-color: #0D1117;
        color: #E6EDF3;
    }
    
    /* Force Sidebar Background Color */
    section[data-testid="stSidebar"] {
        background-color: #0D1117 !important;
        border-right: 1px solid #30363d;
    }
    
    /* Metrics Styling */
    div[data-testid="stMetric"] {
        background-color: #1E293B;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 10px;
    }
    div[data-testid="stMetricLabel"] p { color: #8AC7DE !important; }
    div[data-testid="stMetricValue"] div { color: #FFFFFF !important; }
    h1, h2, h3, h4, h5, h6, p, label { color: #E6EDF3 !important; }
    
    /* Inputs & Dropdowns */
    div[data-baseweb="select"] > div,
    div[data-testid="stDateInput"] > div,
    div[data-baseweb="input"] > div {
        background-color: #1E293B !important;
        border-color: #30363d !important;
        color: #FFFFFF !important;
        font-weight: bold !important;
    }
    input { color: #FFFFFF !important; font-weight: bold !important; }
    
    /* Menus & Popups */
    div[data-baseweb="popover"], div[data-baseweb="menu"], ul[role="listbox"] {
        background-color: #1E293B !important;
        border-color: #30363d !important;
    }
    ul[role="listbox"] > li[role="option"] {
        color: #FFFFFF !important;
        background-color: #1E293B !important;
    }
    ul[role="listbox"] > li[role="option"]:hover,
    ul[role="listbox"] > li[role="option"][aria-selected="true"] {
        background-color: #8AC7DE !important;
        color: #0D1117 !important;
    }
    .stSelectbox svg, .stDateInput svg { fill: #8AC7DE !important; }

    /* Remove Scrollbars Globally */
    ::-webkit-scrollbar { display: none; }

    /* ------------------------------------------------------------------- */
    /* B. DESKTOP MODE (Screens wider than 768px) */
    /* ------------------------------------------------------------------- */
    @media (min-width: 768px) {
        
        /* 1. LOCK SIDEBAR (Fixed position, fixed width, no scroll) */
        section[data-testid="stSidebar"] {
            width: 300px !important;
            min-width: 300px !important;
            max-width: 300px !important;
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            bottom: 0 !important;
            overflow: hidden !important; /* KILL SIDEBAR SCROLL */
            z-index: 100 !important;
        }

        /* 2. KILL THE ARROW (The user cannot close what has no button) */
        button[data-testid="stSidebarCollapseButton"] { display: none !important; }
        div[data-testid="collapsedControl"] { display: none !important; }
        
        /* 3. HIDE HEADER (Cleaner look on desktop) */
        header[data-testid="stHeader"] { display: none !important; }
        div[data-testid="stToolbar"] { display: none !important; }

        /* 4. PUSH MAIN CONTENT (Create safe zone for the fixed sidebar) */
        .main .block-container {
            margin-left: 300px !important;
            padding-left: 2rem !important;
            padding-right: 2rem !important;
            padding-top: 1rem !important;
            max-width: calc(100% - 300px) !important;
        }
    }

    /* ------------------------------------------------------------------- */
    /* C. MOBILE MODE (Screens smaller than 768px) */
    /* ------------------------------------------------------------------- */
    @media (max-width: 767px) {
        /* We leave almost everything alone here so Streamlit works naturally */
        
        /* Ensure Header & Menu Button are visible */
        header[data-testid="stHeader"] {
            display: block !important;
            background-color: #0D1117 !important;
        }
        
        /* Ensure Content sits below header */
        .main .block-container {
            padding-top: 4rem !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. DATA LOADING ---
@st.cache_data(ttl=300)
def load_data():
    try:
        # UPDATED UNIFIED DATA LINK (Using the one from your snippet)
        u_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSBejJoRecA-lq52GgBYkpqFv7LanUurbzcl4Hqd0QRjufGX-2LSSZjAjPg7DeQ9-Q8o_sc3A9y3739/pub?gid=1848266904&single=true&output=csv"
        # History link
        h_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSBejJoRecA-lq52GgBYkpqFv7LanUurbzcl4Hqd0QRjufGX-2LSSZjAjPg7DeQ9-Q8o_sc3A9y3739/pub?gid=970184313&single=true&output=csv"
        
        df_u = pd.read_csv(u_url)
        df_h = pd.read_csv(h_url)
        
        df_u['Date'] = pd.to_datetime(df_u['Date'])
        df_h['Date of Pay'] = pd.to_datetime(df_h['Date of Pay'])
        return df_u, df_h
    except Exception as e:
        # We allow this to return None so the app stops gracefully rather than caching an error
        return None, None

df_unified, df_history = load_data()

if df_unified is None:
    st.error("Connection Error: Please check the Google Sheet links or your internet connection.")
    st.stop()

# --- 4. SIDEBAR CONTROLS ---
with st.sidebar:
    st.header("🛡️ Simulator")
    tickers = sorted(df_unified['Ticker'].unique())
    selected_ticker = st.selectbox("Select Asset", tickers)
    st.markdown("---")
    
    default_date = pd.to_datetime("today") - pd.DateOffset(months=12)
    buy_date = st.date_input("Purchase Date", default_date)
    buy_date = pd.to_datetime(buy_date)
    
    date_mode = st.radio("Simulation End Point:", ["Hold to Present", "Sell on Specific Date"])
    if date_mode == "Sell on Specific Date":
        end_date = st.date_input("Sell Date", pd.to_datetime("today"))
        end_date = pd.to_datetime(end_date)
    else:
        end_date = pd.to_datetime("today")
        
    st.markdown("---")
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

# --- 6. DASHBOARD ---
try:
    meta_row = price_df.iloc[0]
    asset_underlying = meta_row.get('Underlying', '-')
    asset_company = meta_row.get('Company', '-')
except Exception:
    asset_underlying = "-"
    asset_company = "-"

col_head, col_meta = st.columns([3, 1])
with col_head:
    st.markdown(f"### {selected_ticker} Performance Simulator")
    st.markdown(f"**{shares:.2f} shares** | {buy_date.date()} ➝ {end_date.date()}")

with col_meta:
    st.markdown(f"""
        <div style="
            text-align: left; 
            padding: 5px; 
            border-left: 2px solid #30363d; 
            margin-top: 5px;
            padding-left: 15px;">
            <span style="color: #8AC7DE; font-size: 0.8rem;">Underlying</span><br>
            <span style="color: #E6EDF3; font-weight: bold; font-size: 1rem;">{asset_underlying}</span><br>
            <div style="height: 5px;"></div>
            <span style="color: #8AC7DE; font-size: 0.8rem;">Company</span><br>
            <span style="color: #E6EDF3; font-weight: bold; font-size: 1rem;">{asset_company}</span>
        </div>
    """, unsafe_allow_html=True)

m1, m2, m3, m4 = st.columns(4)
m1.metric("Initial Capital", f"${initial_cap:,.2f}")
m2.metric("Market Value", f"${current_market_val:,.2f}", f"{market_pl:,.2f}")
m3.metric("Dividends Collected", f"${cash_total:,.2f}", f"+{cash_total:,.2f}")
m4.metric("True Total Value", f"${current_total_val:,.2f}", f"{total_return_pct:.2f}%")

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
    margin=dict(l=0, r=0, t=20, b=0),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1,
        font=dict(color="#E6EDF3")
    ),
    hovermode="x unified"
)
st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

# Data breakdown
with st.expander("View Data"):
    st.dataframe(
        journey[['Date', 'Closing Price', 'Market_Value', 'Cash_Banked', 'True_Value']]
            .sort_values('Date', ascending=False),
        use_container_width=True,
        height=200
    )
