import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import gspread
from google.oauth2.service_account import Credentials

# --- 1. SETUP PAGE CONFIGURATION ---
st.set_page_config(page_title="Market Breadth Dashboard", layout="wide")
st.title("Market Breadth & Signals")

# --- 2. CONNECT TO GOOGLE SHEETS ---
# We use a function with @st.cache_data so we don't spam Google with requests every time you click a button
@st.cache_data(ttl=600)  # Clears cache every 10 mins (600 seconds)
def load_data():
    # Define the scopes (permissions) we need
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    
    # Load credentials from Streamlit Secrets (we will set this up in Phase 3)
    # The dictionary key here must match what we put in secrets.toml later
    credentials = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=scopes
    )
    
    gc = gspread.authorize(credentials)
    
    # Open the sheet by URL or Name. Replace this with your exact Sheet Name
    sh = gc.open("Your_Google_Sheet_Name_Here") 
    
    # Select the first worksheet
    worksheet = sh.get_worksheet(0)
    
    # Get all records
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)
    
    return df

# --- 3. DATA PROCESSING ---
try:
    df = load_data()

    # Ensure Date is parsed correctly
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Ensure NNHL is numeric (handles potential empty strings or errors)
    df['NNHL'] = pd.to_numeric(df['NNHL'], errors='coerce').fillna(0)

except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# --- 4. VISUALIZATION: NNHL BAR CHART ---

# Create color logic: Green for > 0, Red for < 0
colors = ['#22c55e' if x >= 0 else '#ef4444' for x in df['NNHL']]

fig = go.Figure()

fig.add_trace(go.Bar(
    x=df['Date'],
    y=df['NNHL'],
    name='NNHL',
    marker_color=colors,
    # This makes the bars look cleaner by removing the border lines
    marker_line_width=0 
))

# Styling to match a professional trading terminal look
fig.update_layout(
    title='Net New Highs / Lows (NNHL)',
    xaxis_title='Date',
    yaxis_title='Count',
    template="plotly_dark",  # Dark mode by default
    height=500,
    bargap=0.1 # Slight gap between bars
)

# Render the chart
st.plotly_chart(fig, use_container_width=True)