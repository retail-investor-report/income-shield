import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Income Shield Simulator",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. THE "EMPIRE" STYLING (MARK XVIII: THE HEADS-UP DISPLAY) ---
st.markdown("""
    <style>
    /* Global Text Clean up */
    .stApp {
        background-color: #0D1117;
        color: #E6EDF3;
    }
    
    /* The Custom Header Box */
    .metric-container {
        display: flex;
        flex-direction: row;
        align-items: center;
        background-color: #161B22;
        border-left: 5px solid #8AC7DE;
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 20px;
    }
    
    .ticker-title {
        font-size: 32px;
        font-weight: 800;
        margin-right: 25px;
        color: #FFFFFF;
        line-height: 1;
    }
    
    .badge-group {
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .meta-badge {
        font-size: 14px;
        font-weight: 500;
        color: #8B949E;
        background-color: #21262D;
        padding: 4px 10px;
        border-radius: 4px;
        margin: 2px 0;
        border: 1px solid #30363D;
        width: fit-content;
    }
    
    .highlight {
        color: #8AC7DE;
        font-weight: 700;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATA LOADING (NOW WITH MASTER LIST "THE BRAIN") ---
@st.cache_data(ttl=300)
def load_data():
    try:
        # ⚠️ PASTE YOUR NEW MASTER LIST CSV LINK HERE ⚠️
        m_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSBejJoRecA-lq52GgBYkpqFv7LanUurbzcl4Hqd0QRjufGX-2LSSZjAjPg7DeQ9-Q8o_sc3A9y3739/pub?gid=618318322&single=true&output=csv" 
        
        # Keep your existing links
        u_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSBejJoRecA-lq52GgBYkpqFv7LanUurbzcl4Hqd0QRjufGX-2LSSZjAjPg7DeQ9-Q8o_sc3A9y3739/pub?gid=728728946&single=true&output=csv"
        h_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSBejJoRecA-lq52GgBYkpqFv7LanUurbzcl4Hqd0QRjufGX-2LSSZjAjPg7DeQ9-Q8o_sc3A9y3739/pub?gid=970184313&single=true&output=csv"
        
        df_m = pd.read_csv(m_url)
        df_u = pd.read_csv(u_url)
        df_h = pd.read_csv(h_url)
        
        # Clean Data
        df_u['Date'] = pd.to_datetime(df_u['Date'])
        df_h['Date of Pay'] = pd.to_datetime(df_h['Date of Pay'])
        
        # Normalize Ticker Column Names if needed
        if 'Ticker' not in df_m.columns:
             # Fallback if column A is unnamed or different in Master List
             df_m.rename(columns={df_m.columns[0]: 'Ticker'}, inplace=True)
             
        return df_m, df_u, df_h
    except Exception as e:
        return None, None, None

df_master, df_unified, df_history = load_data()

if df_unified is None:
    st.error("🚨 Link Connection Error: Please check your Google Sheet CSV links (especially the new Master List).")
    st.stop()

# --- 4. SIDEBAR CONTROLS ---
with st.sidebar:
    st.header("🛡️ Simulator")
    
    # Ticker Selection
    tickers = sorted(df_unified['Ticker'].unique())
    selected_ticker = st.selectbox("Select Asset", tickers)
    
    st.markdown("---")
    
    # 1. Start Date
    default_date = pd.to_datetime("today") - pd.DateOffset(months=12)
    buy_date = st.date_input("Purchase Date", default_date)
    buy_date = pd.to_datetime(buy_date)

    # 2. End Date Logic
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
        st.error("No data available for this date range.")
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

# --- 6. DASHBOARD HEADER (THE UPGRADE) ---

# Fetch Metadata from Master List
try:
    meta_row = df_master[df_master['Ticker'] == selected_ticker].iloc[0]
    # Check column names match your CSV exactly, adjust if needed
    underlying = meta_row.get('Underlying Asset', 'Unknown Asset') 
    issuer = meta_row.get('Company', 'Unknown Issuer')
except:
    underlying = "Unknown Asset"
    issuer = "Unknown Issuer"

# Render The Custom Header
st.markdown(f"""
    <div class="metric-container">
        <div class="ticker-title">{selected_ticker} Simulator</div>
        <div class="badge-group">
            <div class="meta-badge">UNDERLYING: <span class="highlight">{underlying}</span></div>
            <div class="meta-badge">ISSUER: <span class="highlight">{issuer}</span></div>
        </div>
    </div>
""", unsafe_allow_html=True)


# Metrics Row
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
    mode='lines', name='Price Only',
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
    st.dataframe(journey[['Date', 'Closing Price', 'Market_Value', 'Cash_Banked', 'True_Value']].sort_values('Date', ascending=False), use_container_width=True, height=200)
