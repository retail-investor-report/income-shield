import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Income Shield Simulator",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. THE STYLING ---
st.markdown("""
    <style>
    /* A. GLOBAL STYLES & LAYOUT FIXES */
    .stApp { background-color: #0D1117; color: #E6EDF3; }
    ::-webkit-scrollbar { display: none !important; }
    
    /* VACUUM SEAL: Remove padding */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }
    .element-container { margin-bottom: 0.2rem !important; }

    /* B. COMPONENT STYLING */
    div[data-testid="stMetric"] {
        background-color: #1E293B;
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 8px 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        min-height: 80px; 
        transition: transform 0.2s;
    }
    
    /* SLOT 4: Annualized Yield (Gold Highlight) */
    div[data-testid="column"]:nth-of-type(4) div[data-testid="stMetric"] {
        background-color: #1a2e35 !important;
        border: 1px solid #F59E0B !important;
    }

    /* SLOT 5: True Total Value (THE BIG ONE) */
    div[data-testid="column"]:nth-of-type(5) div[data-testid="stMetric"] {
        background-color: #0D1117 !important;
        border: 2px solid #00C805 !important;
        transform: scale(1.15); 
        z-index: 10;
        margin-left: 10px;
    }
    div[data-testid="column"]:nth-of-type(5) div[data-testid="stMetricValue"] div {
        font-size: 1.8rem !important;
    }

    /* METRIC TEXT */
    div[data-testid="stMetricLabel"] p { color: #8AC7DE !important; font-size: 0.85rem !important; font-weight: 600 !important; }
    div[data-testid="stMetricValue"] div { color: #FFFFFF !important; font-size: 1.5rem !important; font-weight: 700 !important; }

    /* DELTA (COLORED NUMBERS) STYLING */
    div[data-testid="stMetricDelta"] svg { transform: scale(1.2); }
    div[data-testid="stMetricDelta"] > div {
        font-size: 1.1rem !important; 
        font-weight: 800 !important;
        filter: brightness(1.2);
    }
    
    /* --- TOOLTIP ICON (The Question Mark) --- */
    [data-testid="stMetricLabel"] svg {
        fill: #E6EDF3 !important;
        opacity: 0.9 !important;
        width: 16px !important;
        height: 16px !important;
    }
    [data-testid="stMetricLabel"]:hover svg {
        fill: #F59E0B !important;
        opacity: 1.0 !important;
    }

    /* --- TOOLTIP POPUP BOX FIX --- */
    div[role="tooltip"] {
        background-color: #1E293B !important; 
        color: #FFFFFF !important;             
        border: 1px solid #8AC7DE !important;  
        border-radius: 6px !important;
        font-size: 0.9rem !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.5) !important;
    }
    div[role="tooltip"] > div {
        background-color: #1E293B !important;
    }

    /* =========================================
       THE CALENDAR "EVERYTHING" FIX 
       ========================================= */
    div[data-baseweb="calendar"] { background-color: #1E293B !important; color: #FFFFFF !important; border: 1px solid #30363d !important; }
    div[data-baseweb="calendar"] > div { background-color: #1E293B !important; }
    div[data-baseweb="select"] div { color: #FFFFFF !important; }
    ul[role="listbox"], div[data-baseweb="menu"] { background-color: #1E293B !important; border: 1px solid #30363d !important; }
    li[role="option"] { color: #FFFFFF !important; background-color: #1E293B !important; }
    li[role="option"]:hover, li[role="option"][aria-selected="true"] { background-color: #8AC7DE !important; color: #0D1117 !important; font-weight: bold !important; }
    div[data-baseweb="calendar"] button svg { fill: #8AC7DE !important; }
    div[data-baseweb="calendar"] button { background-color: transparent !important; }
    div[data-baseweb="calendar"] div[role="grid"] div { color: #E6EDF3 !important; }
    div[data-baseweb="calendar"] button[aria-label] { color: #FFFFFF !important; }
    div[data-baseweb="calendar"] [aria-selected="true"] { background-color: #8AC7DE !important; color: #0D1117 !important; font-weight: bold !important; }
    div[data-baseweb="calendar"] [aria-selected="false"]:hover { background-color: #30363d !important; color: #FFFFFF !important; }

    /* TEXT OVERRIDES */
    h1, h2, h3, h4, h5, h6, p, label { color: #E6EDF3 !important; }

    /* INPUTS & SELECTS GLOBAL */
    div[data-baseweb="select"] > div, div[data-testid="stDateInput"] > div, div[data-baseweb="input"] > div, div[data-baseweb="base-input"] {
        background-color: #1E293B !important;
        border-color: #30363d !important;
        color: #FFFFFF !important;
        font-weight: bold !important;
        border-radius: 6px !important;
        min-height: 40px !important;
    }
    input { color: #FFFFFF !important; font-weight: bold !important; }
    .stSelectbox svg, .stDateInput svg { fill: #8AC7DE !important; }

    /* SIDEBAR COMPACTING */
    .stSidebar .element-container { margin-top: 0rem !important; margin-bottom: 0.5rem !important; }
    .stSidebar .stSelectbox, .stSidebar .stDateInput, .stSidebar .stRadio, .stSidebar .stNumberInput { padding-top: 0rem !important; padding-bottom: 0rem !important; }
    .stSidebar .stCheckbox label { font-weight: bold; color: #8AC7DE !important; }

    /* DATAFRAME FIXES */
    div[data-testid="stDataFrame"] { 
        border: 1px solid #30363d; 
        border-radius: 5px; 
        overflow: hidden;
        /* FORCE DARK MODE FOR TABLES */
        color-scheme: dark;
    }
    
    /* >>> NUCLEAR FIX: HIDE COLUMN MENU BUTTONS & SCROLLBARS <<< */
    div[data-testid="stDataFrame"] div[role="columnheader"] button { display: none !important; }
    div[data-testid="stDataFrame"] div[data-testid="stVerticalBlock"] { overflow: hidden !important; }
    div[data-testid="stDataFrame"] ::-webkit-scrollbar { display: none !important; }

    /* C. DESKTOP LAYOUT LOCK (Min-width 1200px) */
    @media (min-width: 1200px) {
        section[data-testid="stSidebar"] {
            width: 300px !important; min-width: 300px !important; height: 100vh !important;
            position: fixed !important; top: 0 !important; left: 0 !important;
            background-color: #0D1117 !important; border-right: 1px solid #30363d !important;
            z-index: 9999 !important; transform: none !important; padding-top: 1rem !important;
        }
        section[data-testid="stSidebar"] h2 { padding-top: 0rem !important; margin-top: 0rem !important; margin-bottom: 1rem !important; }
        section[data-testid="stMain"] { margin-left: 300px !important; width: calc(100% - 300px) !important; position: relative !important; display: block !important; }
        .block-container { padding-left: 3rem !important; padding-right: 3rem !important; padding-top: 1rem !important; padding-bottom: 1rem !important; max-width: 100% !important; }
        header[data-testid="stHeader"], button[data-testid="stSidebarCollapseBtn"], div[data-testid="collapsedControl"] { display: none !important; }
    }

    /* D. MOBILE LAYOUT (Max-width 1199px) */
    @media (max-width: 1199px) {
        section[data-testid="stMain"] { margin-left: 0 !important; width: 100% !important; }
        .block-container { padding-top: 4rem !important; padding-left: 1rem !important; padding-right: 1rem !important; max-width: 100vw !important; min-width: 100vw !important; }
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

# --- HELPER: COMPOUNDING ENGINE ---
def calculate_journey(ticker, start_date, end_date, initial_shares, drip_enabled, unified_df, history_df):
    t_price = unified_df[unified_df['Ticker'] == ticker].sort_values('Date')
    journey = t_price[(t_price['Date'] >= start_date) & (t_price['Date'] <= end_date)].copy()
    
    if journey.empty:
        return journey
        
    t_divs = history_df[history_df['Ticker'] == ticker].sort_values('Date of Pay')
    relevant_divs = t_divs[(t_divs['Date of Pay'] >= start_date) & (t_divs['Date of Pay'] <= end_date)].copy()
    
    journey = journey.set_index('Date')
    journey['Shares'] = initial_shares
    journey['Cash_Pocketed'] = 0.0
    
    current_shares = initial_shares
    cum_cash = 0.0
    
    if not relevant_divs.empty:
        for _, row in relevant_divs.iterrows():
            d_date = row['Date of Pay']
            d_amt = row['Amount']
            
            if d_date in journey.index:
                payout = current_shares * d_amt
                
                if drip_enabled:
                    reinvest_price = journey.loc[d_date, 'Closing Price']
                    new_shares = payout / reinvest_price
                    current_shares += new_shares
                    journey.loc[d_date:, 'Shares'] = current_shares
                else:
                    cum_cash += payout
                    journey.loc[d_date:, 'Cash_Pocketed'] = cum_cash

    journey = journey.reset_index()
    journey['Market_Value'] = journey['Closing Price'] * journey['Shares']
    
    # Base Value = What your initial shares are worth today (No DRIP, No Cash)
    journey['Base_Asset_Value'] = journey['Closing Price'] * initial_shares

    if drip_enabled:
        journey['True_Value'] = journey['Market_Value']
    else:
        journey['True_Value'] = journey['Market_Value'] + journey['Cash_Pocketed']
    
    return journey


# ==========================================
#         SIDEBAR & MODE SELECTION
# ==========================================
with st.sidebar:
    app_mode = st.radio("Select Mode", ["🛡️ Single Asset", "⚔️ Head-to-Head"], label_visibility="collapsed")
    all_tickers = sorted(df_unified['Ticker'].unique())

    # ------------------------------------
    # MODE A: SINGLE ASSET
    # ------------------------------------
    if app_mode == "🛡️ Single Asset":
        selected_ticker = st.selectbox("Select Asset", all_tickers)

        price_df = df_unified[df_unified['Ticker'] == selected_ticker].sort_values('Date')
        if price_df.empty:
            st.error("No data.")
            st.stop()
        
        inception_date = price_df['Date'].min()
        use_inception = st.checkbox("🚀 Start from Inception", value=False)

        if use_inception:
            buy_date = inception_date
            st.markdown(f"<div style='font-size: 0.8rem; color: #8AC7DE; margin-top: -10px; margin-bottom: 10px; font-weight: bold;'>Starting: {buy_date.date()}</div>", unsafe_allow_html=True)
        else:
            default_date = pd.to_datetime("today") - pd.DateOffset(months=12)
            if default_date < inception_date: default_date = inception_date
            buy_date = st.date_input("Purchase Date", default_date)
        
        buy_date = pd.to_datetime(buy_date)
        
        date_mode = st.radio("Simulation End:", ["Hold to Present", "Sell on Specific Date"])
        if date_mode == "Sell on Specific Date":
            end_date = st.date_input("Sell Date", pd.to_datetime("today"))
            end_date = pd.to_datetime(end_date)
        else:
            end_date = pd.to_datetime("today")
            
        mode = st.radio("Input Method:", ["Share Count", "Dollar Amount"])
        
        # MOVED DRIP TOGGLE HERE (Under Input Method)
        use_drip = st.checkbox("🔄 Enable DRIP", value=False, help="Reinvests all dividends back into shares.")

        # Initial Share Calculation
        temp_journey = price_df[(price_df['Date'] >= buy_date) & (price_df['Date'] <= end_date)]
        if not temp_journey.empty:
            entry_price = temp_journey.iloc[0]['Closing Price']
            if mode == "Share Count":
                initial_shares = st.number_input("Shares Owned", min_value=1, value=10)
                sim_amt = initial_shares * entry_price # approx
            else:
                dollars = st.number_input("Amount Invested ($)", min_value=100, value=1000, step=100)
                initial_shares = float(dollars) / entry_price
                sim_amt = dollars
            st.info(f"Entry Price: ${entry_price:.2f}")
        else:
            st.error("No data for date range.")
            st.stop()

    # ------------------------------------
    # MODE B: HEAD-TO-HEAD
    # ------------------------------------
    else:
        selected_tickers = st.multiselect("Select Assets to Compare", all_tickers, default=all_tickers[:2] if len(all_tickers) > 1 else all_tickers)
        
        st.markdown("##### Common Date Range")
        default_start = pd.to_datetime("today") - pd.DateOffset(months=12)
        buy_date = st.date_input("Start Date", default_start)
        buy_date = pd.to_datetime(buy_date)
        end_date = st.date_input("End Date", pd.to_datetime("today"))
        end_date = pd.to_datetime(end_date)

        st.markdown("##### Comparison Inputs")
        sim_amt = st.number_input("Hypothetical Investment ($)", value=10000, step=1000)
        
        # MOVED DRIP TOGGLE HERE (Under Amount)
        use_drip = st.checkbox("🔄 Enable DRIP", value=False, help="Reinvests all dividends back into shares.")
        
        st.info(f"Leaderboard assumes ${sim_amt:,.0f} invested in each.")


# ==========================================
#           MAIN PAGE LOGIC
# ==========================================

# >>>>>>>>>>>>>>> MODE A: SINGLE ASSET DASHBOARD <<<<<<<<<<<<<<<
if app_mode == "🛡️ Single Asset":
    
    journey = calculate_journey(selected_ticker, buy_date, end_date, initial_shares, use_drip, df_unified, df_history)
    
    initial_cap = entry_price * initial_shares
    current_market_val = journey.iloc[-1]['Market_Value']
    cash_total = journey.iloc[-1]['Cash_Pocketed']
    current_total_val = journey.iloc[-1]['True_Value']
    final_shares = journey.iloc[-1]['Shares']

    market_pl = current_market_val - initial_cap
    market_pl_pct = (market_pl / initial_cap) * 100 if initial_cap != 0 else 0
    total_pl = current_total_val - initial_cap
    total_return_pct = (total_pl / initial_cap) * 100

    days_held = (end_date - buy_date).days
    annual_yield = (cash_total/initial_cap)*(365.25/days_held)*100 if days_held > 0 else 0

    # 2. HEADER
    try:
        meta_row = df_unified[df_unified['Ticker'] == selected_ticker].iloc[0]
        asset_underlying = meta_row.get('Underlying', '-')
        asset_company = meta_row.get('Company', '-')
    except:
        asset_underlying, asset_company = "-", "-"

    col_head, col_meta = st.columns([1.8, 1.2])
    with col_head:
        st.markdown(f"""
            <div style="margin-top: -10px;">
                <h1 style="font-size: 2.5rem; margin-bottom: 0px; color: #E6EDF3; line-height: 1.2;">
                    {selected_ticker} <span style="color: #8AC7DE;">Performance Simulator</span>
                </h1>
                <p style="font-size: 1.1rem; color: #8AC7DE; opacity: 0.8; margin-top: -5px; margin-bottom: 10px;">
                    <b>{final_shares:.2f} shares</b> &nbsp;|&nbsp; {buy_date.date()} ➝ {end_date.date()} ({days_held} days)
                </p>
            </div>
        """, unsafe_allow_html=True)
    with col_meta:
        st.markdown(f"""
            <div style="display: flex; gap: 8px; justify-content: flex-end; align-items: center; height: 100%; padding-top: 5px;">
                <div style="background: rgba(30, 41, 59, 0.7); border: 1px solid #30363d; border-radius: 8px; padding: 8px 12px; text-align: center; min-width: 80px; flex-grow: 1;">
                    <div style="color: #8AC7DE; font-size: 0.7rem; text-transform: uppercase;">Underlying</div>
                    <div style="color: white; font-size: 1.1rem; font-weight: 800;">{asset_underlying}</div>
                </div>
                <div style="background: rgba(30, 41, 59, 0.7); border: 1px solid #30363d; border-radius: 8px; padding: 8px 12px; text-align: center; min-width: 80px; flex-grow: 1;">
                    <div style="color: #8AC7DE; font-size: 0.7rem; text-transform: uppercase;">Company</div>
                    <div style="color: white; font-size: 1.1rem; font-weight: 800;">{asset_company}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    # 3. METRICS
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Initial Capital", f"${initial_cap:,.2f}")
    
    val_label = "End Asset Value" if not use_drip else "End Value (DRIP)"
    cash_label = "Dividends Collected" if not use_drip else "New Shares Acquired"
    
    # Calculate delta string with percentage
    asset_delta_str = f"{market_pl:,.2f} ({market_pl_pct:+.2f}%)"
    m2.metric(val_label, f"${current_market_val:,.2f}", asset_delta_str)
    
    if use_drip:
        shares_gained = final_shares - initial_shares
        m3.metric(cash_label, f"{shares_gained:.2f} Shares")
        m4.metric("Effective Yield", "N/A (Reinvested)")
    else:
        m3.metric(cash_label, f"${cash_total:,.2f}") 
        m4.metric("Annualized Yield", f"{annual_yield:.2f}%")

    m5.metric("True Total Value", f"${current_total_val:,.2f}", f"{total_return_pct:.2f}%")

    # 4. SINGLE CHART (Restored Logic)
    fig = go.Figure()
    
    # Trace A: The "Bottom" Line (Reference)
    # If DRIP OFF: This is Market Value (Price Action)
    # If DRIP ON:  This is Base Asset Value (What it would be without DRIP)
    bottom_y = journey['Market_Value'] if not use_drip else journey['Base_Asset_Value']
    
    # Trace B: The "Top" Line (Total Return)
    top_y = journey['True_Value']
    
    # 1. Plot Bottom Line (Reference)
    price_color = '#8AC7DE' if journey.iloc[-1]['Closing Price'] >= journey.iloc[0]['Closing Price'] else '#FF4B4B'
    fig.add_trace(go.Scatter(
        x=journey['Date'], y=bottom_y, 
        mode='lines', name='Asset Price', 
        line=dict(color=price_color, width=2) # Solid line for base
    ))

    # 2. Plot Top Line (Total Value) with FILL to the Bottom Line
    fig.add_trace(go.Scatter(
        x=journey['Date'], y=top_y, 
        mode='lines', name='True Value', 
        line=dict(color='#00C805', width=3), 
        fill='tonexty', # This fills the gap between this line and the previous one (Asset Price)
        fillcolor='rgba(0, 200, 5, 0.1)'
    ))
    
    fig.add_hline(y=initial_cap, line_dash="dash", line_color="white", opacity=0.3)

    profit_text = f"PROFIT: +${total_pl:,.2f}" if total_pl >= 0 else f"LOSS: -${abs(total_pl):,.2f}"
    profit_bg = "#00C805" if total_pl >= 0 else "#FF4B4B"

    fig.add_annotation(
        x=0.02, y=0.95, xref="paper", yref="paper", text=profit_text, showarrow=False,
        font=dict(family="Arial Black, sans-serif", size=16, color="white"),
        bgcolor=profit_bg, bordercolor=profit_bg, borderpad=8, opacity=0.9, align="left"
    )

    fig.update_layout(
        template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        height=340, margin=dict(l=0, r=0, t=20, b=0), showlegend=False, hovermode="x unified",
        xaxis=dict(fixedrange=True), yaxis=dict(fixedrange=True)
    )
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    # 5. LEGEND DECODER
    st.markdown("""
        <div style="background-color: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 5px 8px; text-align: center;">
            <span style="color: #00C805; font-weight: 800;">💚 True Value (Total Equity)</span> &nbsp;&nbsp;
            <span style="color: #8AC7DE; font-weight: 800;">🔵 Price Appreciation</span> &nbsp;&nbsp;
            <span style="color: #FF4B4B; font-weight: 800;">🔴 Price Erosion</span>
        </div>
    """, unsafe_allow_html=True)
    
    with st.expander("View Data"):
        st.dataframe(journey.sort_values('Date', ascending=False), use_container_width=True)


# >>>>>>>>>>>>>>> MODE B: HEAD-TO-HEAD COMPARISON <<<<<<<<<<<<<<<
else:
    # --------------------------------------------------------
    # RESTORED TITLE STYLE: Standard Markdown (White + Blue)
    # --------------------------------------------------------
    st.markdown("""
        <div style="margin-top: -10px; margin-bottom: 20px;">
            <h1 style="font-size: 2.5rem; margin-bottom: 0px; color: #E6EDF3; line-height: 1.2;">
                ⚔️ Head-to-Head <span style="color: #8AC7DE;">Comparison</span>
            </h1>
        </div>
    """, unsafe_allow_html=True)
    
    if not selected_tickers:
        st.warning("Please select at least one asset in the sidebar.")
        st.stop()
        
    comp_data = []
    fig_comp = go.Figure()
    
    colors = ['#00C805', '#F59E0B', '#8AC7DE', '#FF4B4B', '#A855F7', '#EC4899', '#EAB308']
    
    for idx, t in enumerate(selected_tickers):
        t_price_check = df_unified[df_unified['Ticker'] == t].sort_values('Date')
        t_price_check = t_price_check[(t_price_check['Date'] >= buy_date) & (t_price_check['Date'] <= end_date)]
        
        if t_price_check.empty:
            continue
            
        start_p = t_price_check.iloc[0]['Closing Price']
        initial_s = sim_amt / start_p
        
        t_journey = calculate_journey(t, buy_date, end_date, initial_s, use_drip, df_unified, df_history)
        
        if t_journey.empty:
            continue

        initial_cap = sim_amt
        t_journey['Total_Return_Pct'] = ((t_journey['True_Value'] - initial_cap) / initial_cap) * 100
        
        line_color = colors[idx % len(colors)]
        fig_comp.add_trace(go.Scatter(
            x=t_journey['Date'], 
            y=t_journey['Total_Return_Pct'], 
            mode='lines', 
            name=t,
            line=dict(color=line_color, width=3)
        ))
        
        final_row = t_journey.iloc[-1]
        final_ret = final_row['Total_Return_Pct']
        
        end_value = final_row['Market_Value']
        cash_generated = final_row['Cash_Pocketed']
        final_total = final_row['True_Value']
        
        if not use_drip:
            yield_pct = (cash_generated / initial_cap) * 100
        else:
            yield_pct = 0.0
        
        shares_added = final_row['Shares'] - initial_s
        
        data_row = {
            "Ticker": t,
            "Total Return": final_ret,
            "💚 Total Value": final_total
        }
        
        if use_drip:
            data_row["📈 New Shares Added"] = shares_added
            data_row["Yield %"] = "N/A"
        else:
            data_row["💰 Cash Generated"] = cash_generated
            data_row["Yield %"] = yield_pct
            data_row["📉 Share Value (Remaining)"] = end_value

        comp_data.append(data_row)
        
    fig_comp.add_hline(y=0, line_dash="solid", line_color="white", opacity=0.5, annotation_text="Break Even")
    
    fig_comp.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=400,
        margin=dict(l=0, r=0, t=30, b=0),
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color="white")),
        yaxis_title="Total Return (%)",
        xaxis=dict(fixedrange=True), yaxis=dict(fixedrange=True)
    )
    
    st.plotly_chart(fig_comp, use_container_width=True, config={'displayModeBar': False})
    
    if comp_data:
        st.markdown(f"### 🏆 Leaderboard (${sim_amt:,.0f} Investment)")
        df_comp = pd.DataFrame(comp_data).sort_values("Total Return", ascending=False)
        
        df_display = df_comp.copy()
        df_display['Total Return'] = df_display['Total Return'].apply(lambda x: f"{x:+.2f}%")
        df_display['💚 Total Value'] = df_display['💚 Total Value'].apply(lambda x: f"${x:,.2f}")
        
        if use_drip:
             df_display['📈 New Shares Added'] = df_display['📈 New Shares Added'].apply(lambda x: f"{x:.2f}")
             cols = ["Ticker", "Total Return", "📈 New Shares Added", "💚 Total Value"]
        else:
             df_display['Yield %'] = df_display['Yield %'].apply(lambda x: f"{x:.2f}%")
             df_display['💰 Cash Generated'] = df_display['💰 Cash Generated'].apply(lambda x: f"${x:,.2f}")
             df_display['📉 Share Value (Remaining)'] = df_display['📉 Share Value (Remaining)'].apply(lambda x: f"${x:,.2f}")
             cols = ["Ticker", "Total Return", "Yield %", "💰 Cash Generated", "📉 Share Value (Remaining)", "💚 Total Value"]

        st.dataframe(
            df_display, 
            column_order=cols,
            hide_index=True,
            use_container_width=True
        )
