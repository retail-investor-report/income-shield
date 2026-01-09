import streamlit as st
import pandas as pd
import os

# --- PAGE SETTINGS ---
st.set_page_config(layout="wide", page_title="RDI Terminal", initial_sidebar_state="expanded")

# --- VISUAL FIXES (CSS) ---
# This forces the sidebar to stay OPEN and hides the collapse arrow
st.markdown("""
<style>
    /* 1. HIDE THE SIDEBAR COLLAPSE ARROW */
    [data-testid="stSidebarCollapsedControl"] {
        display: none; 
    }
    
    /* 2. FORCE DARK MODE & HIGH CONTRAST TEXT */
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    h1, h2, h3, p, div, span {
        color: #ffffff !important;
    }
    
    /* 3. TABLE STYLING */
    [data-testid="stDataFrame"] {
        border: 1px solid #333;
    }
    
    /* 4. SIDEBAR BACKGROUND */
    [data-testid="stSidebar"] {
        background-color: #161b22;
        border-right: 1px solid #333;
    }
</style>
""", unsafe_allow_html=True)

# --- FILE CONFIGURATION ---
# These must match the filenames you upload to GitHub
FILES = {
    "📊 Dashboard": "The Retail Dividend Investor Spreadsheet - Master List.csv",
    "🏆 Winner of Week": "The Retail Dividend Investor Spreadsheet - Winner of The Week.csv",
    "🚀 YieldMax": "The Retail Dividend Investor Spreadsheet - YieldMax (All).csv",
    "🛡️ Defiance": "The Retail Dividend Investor Spreadsheet - Defiance (All).csv",
    "🎯 Roundhill": "The Retail Dividend Investor Spreadsheet - Roundhill (All).csv",
    "🆕 Newest Funds": "The Retail Dividend Investor Spreadsheet - Newest Funds.csv"
}

# --- DATA LOADING ENGINE ---
def load_data(filename):
    """
    Loads CSVs safely. If the file isn't found (e.g., hasn't been uploaded yet),
    it handles the error gracefully so the app doesn't crash.
    """
    if not os.path.exists(filename):
        return None
    
    try:
        # Smart load: looks for the header row automatically
        preview = pd.read_csv(filename, header=None, nrows=10)
        header_row = 0
        for i, row in preview.iterrows():
            # If we find "Ticker" or "Yield" in the row, that's our header
            if row.astype(str).str.contains('Ticker|Yield|Price', case=False).any():
                header_row = i
                break
        
        df = pd.read_csv(filename, header=header_row)
        
        # Basic cleanup: Remove empty columns
        df = df.dropna(axis=1, how='all')
        return df
    except:
        return None

# --- SIDEBAR NAVIGATION ---
st.sidebar.header("RDI TERMINAL")
st.sidebar.markdown("---")

# The menu
menu_options = list(FILES.keys())
selection = st.sidebar.radio("Select Data View", menu_options)

st.sidebar.markdown("---")
st.sidebar.info("✅ Sidebar Locked\n✅ High Contrast")

# --- MAIN CONTENT AREA ---
st.title(selection)

selected_file = FILES[selection]
df = load_data(selected_file)

if df is not None:
    # Display the data in a sortable, clean table
    st.dataframe(
        df, 
        use_container_width=True, 
        height=800,
        hide_index=True
    )
else:
    # Friendly error if file is missing
    st.error(f"⚠️ Data file not found: {selected_file}")
    st.caption("Make sure you uploaded the CSV files to your GitHub repository.")
