import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="RDI Terminal",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS HACKS FOR "FIXED SIDEBAR" & HIGH CONTRAST ---
st.markdown("""
<style>
    /* 1. HIDE SIDEBAR COLLAPSE ARROW (Locks sidebar open on Desktop) */
    [data-testid="stSidebarCollapsedControl"] {
        display: none;
    }

    /* 2. FORCE TEXT COLORS (High Contrast) */
    h1, h2, h3, p, div, span, label {
        color: #FFFFFF !important;
    }
    
    /* Muted text for secondary info */
    .small-text {
        color: #b0b0b0 !important;
    }

    /* 3. TABLE STYLING */
    [data-testid="stDataFrame"] {
        border: 1px solid #444;
    }
</style>
""", unsafe_allow_html=True)

# --- FILE MAPPING (Your CSV Inventory) ---
# Update these filenames if they change slightly on your disk
FILES = {
    "📊 Master Dashboard": "The Retail Dividend Investor Spreadsheet - Master List.csv",
    "🏆 Winner of The Week": "The Retail Dividend Investor Spreadsheet - Winner of The Week.csv",
    "🚀 YieldMax (All)": "The Retail Dividend Investor Spreadsheet - YieldMax (All).csv",
    "🛡️ Defiance": "The Retail Dividend Investor Spreadsheet - Defiance (All).csv",
    "🎯 Roundhill": "The Retail Dividend Investor Spreadsheet - Roundhill (All).csv",
    "🦖 Rex Shares": "The Retail Dividend Investor Spreadsheet - Rex Shares (All).csv",
    "🌑 NEOS": "The Retail Dividend Investor Spreadsheet - NEOS.csv",
    "🏦 Goldman Sachs": "The Retail Dividend Investor Spreadsheet - Goldman-Sachs.csv",
    "📈 ProShares": "The Retail Dividend Investor Spreadsheet - ProShares.csv",
    "🌐 Global X": "The Retail Dividend Investor Spreadsheet - Global-X-ETF's.csv",
    "⛏️ Granite Shares": "The Retail Dividend Investor Spreadsheet - Granite-Shares-Yieldboost.csv",
    "⚡ Kurv": "The Retail Dividend Investor Spreadsheet - Kurv-Investment-Management-LLC.csv",
    "🆕 Newest Funds": "The Retail Dividend Investor Spreadsheet - Newest Funds.csv"
}

# --- SMART DATA LOADER ---
def load_data(filepath):
    """
    Smartly reads CSVs even if they have junk rows at the top.
    Finds the row containing 'Inception' or 'Ticker' and uses that as header.
    """
    if not os.path.exists(filepath):
        return None

    # First, try to find the header row
    try:
        # Read first 10 rows to inspect
        preview = pd.read_csv(filepath, header=None, nrows=10)
        header_row_index = 0
        
        for idx, row in preview.iterrows():
            row_str = row.astype(str).str.lower().tolist()
            # Look for keywords that indicate the header line
            if any(x in row_str for x in ['inception', 'underlying asset', 'current price', 'dividend']):
                header_row_index = idx
                break
        
        # Load the actual data with the correct header
        df = pd.read_csv(filepath, header=header_row_index)
        
        # CLEANUP: Rename the weird empty first column if it exists
        if df.columns[0] == '`' or 'Unnamed' in str(df.columns[0]):
             df.rename(columns={df.columns[0]: 'Ticker'}, inplace=True)
        
        # CLEANUP: Convert Yield % Strings to Numbers for Sorting
        # Finds columns with "Dividend" or "Yield" in name
        for col in df.columns:
            if 'Dividend' in col or 'Yield' in col:
                # Remove % sign and convert to float
                df[col] = df[col].astype(str).str.replace('%', '', regex=False)
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
        
    except Exception as e:
        st.error(f"Error reading file: {e}")
        return None

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("RDI Terminal")
st.sidebar.caption("The Retail Dividend Investor")
st.sidebar.markdown("---")

selected_view = st.sidebar.radio(
    "Select Data Set",
    list(FILES.keys()),
    index=0
)

st.sidebar.markdown("---")
st.sidebar.info("Sidebar is locked for desktop view.")

# --- MAIN CONTENT ---
st.title(selected_view)

filename = FILES[selected_view]
df = load_data(filename)

if df is not None:
    # Top KPI Metrics (if data allows)
    col1, col2, col3 = st.columns(3)
    
    # Calculate some quick stats if columns exist
    if 'Dividend' in df.columns:
        avg_yield = df['Dividend'].mean()
        max_yield = df['Dividend'].max()
        top_payer = df.loc[df['Dividend'].idxmax(), 'Ticker'] if 'Ticker' in df.columns else "N/A"
        
        col1.metric("Average Yield", f"{avg_yield:.2f}%")
        col2.metric("Highest Yield", f"{max_yield:.2f}%")
        col3.metric("Top Payer", top_payer)

    st.markdown("---")

    # Data Display
    # We use data_editor to allow sorting and column resizing, but disabled editing
    st.data_editor(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Dividend": st.column_config.ProgressColumn(
                "Annual Yield (%)",
                format="%.2f%%",
                min_value=0,
                max_value=200, # Cap progress bar at 200% for visual sanity
            ),
            "Current Price": st.column_config.NumberColumn(
                "Price ($)",
                format="$%.2f"
            ),
            "Latest Distribution ": st.column_config.NumberColumn(
                "Payout ($)",
                format="$%.4f"
            ),
            "Inception": st.column_config.DateColumn(
                "Inception Date",
                format="MM/DD/YYYY"
            )
        },
        height=800
    )
    
else:
    st.warning(f"File not found: {filename}. Please ensure the CSV is in the directory.")
    st.markdown("### Debug Info")
    st.write(f"Looking for: {os.getcwd()}/{filename}")
