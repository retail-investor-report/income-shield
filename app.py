import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- 1. FORCED PAGE CONFIG ---
st.set_page_config(
    page_title="Income Shield Simulator", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# --- 2. THE "EMPIRE" STYLING (Forced Dark Mode & UI Cleanup) ---
st.markdown("""
    <style>
    /* Force Dark Background for the whole app */
    .stApp {
        background-color: #0E1117;
        color: #FFFFFF;
    }
    /* Force Sidebar to be dark and visible */
    [data-testid="stSidebar"] {
        background-color: #161B22;
        border-right: 1px solid #30363d;
    }
    /* Metric Card Styling */
    div[data-testid="stMetric"] {
        background-color: #1f2937;
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #374151;
    }
    /* Hide the annoying Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .viewerBadge_container__1QSob {display: none !important;}
    
    /* Make Metric text white */
    [data-testid="stMetricValue"] { color: #ffffff !important; }
    [data-testid="stMetricLabel"] { color: #9ca3af !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATA ENGINE ---
@st.cache_data(ttl=600)
def load_data():
    try:
        # PASTE YOUR LINKS HERE
        sheet_url_unified = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSBejJoRecA-lq52GgBYkpqFv7LanUurbzcl4Hqd0QRjufGX-2LSSZjAjPg7DeQ9-Q8o_sc3A9y3739/pub?gid=728728946&single=true&output=csv"
        sheet_url_history = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSBejJoRecA-lq52GgBYkpqFv7LanUurbzcl4Hqd0QRjufGX-2LSSZjAjPg7DeQ9-Q8o_sc3A9y3739/pub?gid=970184313&single=true&output=csv"
        
        df_u = pd.read_csv(sheet_url_unified)
        df_h = pd.read_csv(sheet_url_history)
        df_u['Date'] = pd.to_datetime(df_u['Date'])
        df_h['Date of Pay'] = pd.to_datetime(df_h['Date of Pay'])
        return df_u, df_h
    except:
        return None, None

df_unified, df_history = load_data()

if df_unified is None:
    st.error("🚨 Link Error: Please check your Google Sheet 'Publish to Web' links.")
    st.stop()

# --- 4. SIDEBAR (The Control Center) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135706.png", width=50) # Generic Icon
    st.header("Simulator Settings")
    
    tickers = sorted(df_unified['Ticker'].unique())
    selected_ticker = st.selectbox("Select Fund", tickers)
    
    start_date = st.date_input("Your Buy Date", pd.to_datetime("2025-01-01"))
    start_date = pd.to_datetime(start_date)

    st.markdown("---")
    st.subheader("Position Size")
    invest_type = st.radio("Mode:", ["Shares", "Dollars"])
    
    price_df = df_unified[df_unified['Ticker'] == selected_ticker].sort_values('Date')
    temp_journey = price_df[price_df['Date'] >= start_date]
    
    if not temp_journey.empty:
        buy_price_unit = temp_journey.iloc[0]['Closing Price']
        if invest_type == "Shares":
            num_shares = st.number_input("Shares Owned:", min_value=1, value=1)
        else:
            dollars = st.number_input("Cash Invested ($):", min_value=100, value=1000, step=100)
            num_shares = float(dollars) / buy_price_unit
    else:
        st.warning("No data for this date.")
        st.stop()

# --- 5. MATH ENGINE ---
my_journey = temp_journey.copy()
div_df = df_history[df_history['Ticker'] == selected_ticker].sort_values('Date of Pay')
relevant_divs = div_df[div_df['Date of Pay'] >= start_date].copy()
relevant_divs['CumCash_Unit'] = relevant_divs['Amount'].cumsum()

def get_cash_unit(d):
    d_divs = relevant_divs[relevant_divs['Date of Pay'] <= d]
    return d_divs['CumCash_Unit'].iloc[-1] if not d_divs.empty else 0.0

my_journey['Cash_Unit'] = my_journey['Date'].apply(get_cash_unit)
my_journey['Market_Val'] = my_journey['Closing Price'] * num_shares
my_journey['Total_Cash'] = my_journey['Cash_Unit'] * num_shares
my_journey['True_Val'] = my_journey['Market_Val'] + my_journey['Total_Cash']

# Statistics
initial = buy_price_unit * num_shares
final_true = my_journey.iloc[-1]['True_Val']
final_cash = my_journey.iloc[-1]['Total_Cash']
total_ret_pct = ((final_true - initial) / initial) * 100

# --- 6. MAIN INTERFACE ---
st.title(f"🛡️ {selected_ticker} Income Shield")
st.write(f"Investing **${initial:,.2f}** on **{start_date.date()}**")

# Metrics
c1, c2, c3, c4 = st.columns(4)
c1.metric("Initial Capital", f"${initial:,.2f}")
c2.metric("Market Value", f"${my_journey.iloc[-1]['Market_Val']:,.2f}")
c3.metric("Dividends Paid", f"${final_cash:,.2f}")
c4.metric("True Balance", f"${final_true:,.2f}", f"{total_ret_pct:.2f}%")

# --- 7. THE "PRO" CHART ---
fig = go.Figure()

# Market Value Line (Lower boundary)
fig.add_trace(go.Scatter(
    x=my_journey['Date'], y=my_journey['Market_Val'],
    mode='lines', name='Price Action',
    line=dict(color='#FF4B4B', width=1),
))

# True Value Line (Upper boundary)
fig.add_trace(go.Scatter(
    x=my_journey['Date'], y=my_journey['True_Val'],
    mode='lines', name='Total Return (Price + Divs)',
    line=dict(color='#00C805', width=3),
    fill='tonexty', # THIS CREATES THE SHADING EFFECT
    fillcolor='rgba(0, 200, 5, 0.15)' 
))

# Break Even Dotted Line
fig.add_hline(y=initial, line_dash="dash", line_color="#888888", opacity=0.5)

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
