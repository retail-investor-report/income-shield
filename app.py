import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- PAGE SETUP ---
st.set_page_config(page_title="Income Shield Simulator", layout="wide", initial_sidebar_state="expanded")

# --- CUSTOM CSS ---
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;} 
            footer {visibility: hidden;} 
            header {visibility: hidden;} 
            [data-testid="stSidebarCollapseBtn"] {display: none;}
            .viewerBadge_container__1QSob {display: none !important;} 
            [data-testid="stStatusWidget"] {display: none !important;}
            div[data-testid="stMetric"] {
                background-color: #1e1e1e;
                padding: 10px;
                border-radius: 10px;
                text-align: center;
                border: 1px solid #333;
            }
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# --- LOAD LIVE DATA FROM GOOGLE SHEETS ---
@st.cache_data(ttl=600) # Clears cache every 10 mins so data stays fresh
def load_data():
    try:
        # ---------------------------------------------------------
        # PASTE YOUR GOOGLE SHEET LINKS BETWEEN THE QUOTES BELOW
        # ---------------------------------------------------------
        sheet_url_unified = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSBejJoRecA-lq52GgBYkpqFv7LanUurbzcl4Hqd0QRjufGX-2LSSZjAjPg7DeQ9-Q8o_sc3A9y3739/pub?gid=728728946&single=true&output=csv"
        sheet_url_history = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSBejJoRecA-lq52GgBYkpqFv7LanUurbzcl4Hqd0QRjufGX-2LSSZjAjPg7DeQ9-Q8o_sc3A9y3739/pub?gid=970184313&single=true&output=csv"
        
        # Read directly from the web
        df_u = pd.read_csv(sheet_url_unified)
        df_h = pd.read_csv(sheet_url_history)
        
        # Date Conversion
        df_u['Date'] = pd.to_datetime(df_u['Date'])
        df_h['Date of Pay'] = pd.to_datetime(df_h['Date of Pay'])
        return df_u, df_h
    except Exception as e:
        return None, None

df_unified, df_history = load_data()

if df_unified is None:
    st.error("Error: Could not read data. Please check that you pasted the 'Publish to Web' CSV links correctly in app.py.")
    st.stop()

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Ticker Selector
    tickers = sorted(df_unified['Ticker'].unique())
    selected_ticker = st.selectbox("Select Fund", tickers)
    
    # Date Selector
    start_date = st.date_input("When did you buy?", pd.to_datetime("today") - pd.DateOffset(months=6))
    start_date = pd.to_datetime(start_date)

    st.markdown("---")
    
    # Investment Amount Input
    st.subheader("💰 Investment Size")
    invest_type = st.radio("Input Method:", ["Share Count", "Dollar Amount"])
    
    num_shares = 1.0 
    
    price_df = df_unified[df_unified['Ticker'] == selected_ticker].sort_values('Date')
    temp_journey = price_df[price_df['Date'] >= start_date]
    
    if not temp_journey.empty:
        buy_price_unit = temp_journey.iloc[0]['Closing Price']
        
        if invest_type == "Share Count":
            user_shares = st.number_input("Number of Shares:", min_value=1, value=1, step=1)
            num_shares = float(user_shares)
            display_invested = num_shares * buy_price_unit
        else:
            user_dollars = st.number_input("Dollar Amount ($):", min_value=100, value=1000, step=100)
            num_shares = float(user_dollars) / buy_price_unit
            display_invested = float(user_dollars)
            st.caption(f"At ${buy_price_unit:.2f}/share, you bought {num_shares:.2f} shares.")
    else:
        st.warning("No data for this date.")
        st.stop()

# --- CALCULATIONS ---
my_journey = temp_journey.copy()
buy_price_unit = my_journey.iloc[0]['Closing Price']

div_df = df_history[df_history['Ticker'] == selected_ticker].sort_values('Date of Pay')
relevant_divs = div_df[div_df['Date of Pay'] >= start_date].copy()
relevant_divs['CumCash_Unit'] = relevant_divs['Amount'].cumsum()

def get_cash_unit(d):
    d_divs = relevant_divs[relevant_divs['Date of Pay'] <= d]
    return d_divs['CumCash_Unit'].iloc[-1] if not d_divs.empty else 0.0

my_journey['Cash_Unit'] = my_journey['Date'].apply(get_cash_unit)
my_journey['TotalValue_Unit'] = my_journey['Closing Price'] + my_journey['Cash_Unit']

# Scale by Shares
my_journey['Portfolio Value'] = my_journey['Closing Price'] * num_shares
my_journey['Total Cash Collected'] = my_journey['Cash_Unit'] * num_shares
my_journey['True Portfolio Value'] = my_journey['TotalValue_Unit'] * num_shares

# Metrics
curr_val = my_journey.iloc[-1]['Portfolio Value']
total_cash = my_journey.iloc[-1]['Total Cash Collected']
true_val = my_journey.iloc[-1]['True Portfolio Value']
initial_investment = buy_price_unit * num_shares
total_return_pct = ((true_val - initial_investment) / initial_investment) * 100

# --- MAIN DISPLAY ---
st.title(f"🛡️ {selected_ticker} Income Simulator")
st.markdown(f"**Scenario:** You invested **${initial_investment:,.2f}** ({num_shares:.2f} shares) on **{start_date.date()}**.")

# Metric Row
c1, c2, c3, c4 = st.columns(4)
c1.metric("Initial Investment", f"${initial_investment:,.2f}")
c2.metric("Current Market Value", f"${curr_val:,.2f}", delta=f"${curr_val - initial_investment:,.2f}")
c3.metric("Cash Dividends Collected", f"${total_cash:,.2f}")
c4.metric("True Portfolio Value", f"${true_val:,.2f}", delta=f"{total_return_pct:.2f}%")

# Chart
fig = go.Figure()

# Market Value (Red)
fig.add_trace(go.Scatter(
    x=my_journey['Date'], y=my_journey['Portfolio Value'],
    mode='lines', name='Market Value (Price Only)',
    line=dict(color='#ff4b4b', width=2),
    fill='tozeroy', fillcolor='rgba(255, 75, 75, 0.1)',
    hovertemplate='$%{y:,.2f}'
))

# True Value (Green)
fig.add_trace(go.Scatter(
    x=my_journey['Date'], y=my_journey['True Portfolio Value'],
    mode='lines', name='True Value (With Dividends)',
    line=dict(color='#00c805', width=3),
    hovertemplate='$%{y:,.2f}'
))

# Break Even
fig.add_hline(y=initial_investment, line_dash="dash", line_color="gray", annotation_text="Break Even")

fig.update_layout(
    height=500, 
    hovermode="x unified", 
    template="plotly_dark",
    margin=dict(l=0, r=0, t=30, b=0),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)'
)
st.plotly_chart(fig, use_container_width=True)

with st.expander("See Daily Breakdown Data"):
    st.dataframe(my_journey[['Date', 'Closing Price', 'Portfolio Value', 'Total Cash Collected', 'True Portfolio Value']].sort_values('Date', ascending=False))