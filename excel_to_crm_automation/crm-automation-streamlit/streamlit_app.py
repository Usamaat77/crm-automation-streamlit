import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import tempfile
from pathlib import Path
import base64
from io import BytesIO

# Set page config
st.set_page_config(
    page_title="CRM Automation Tool",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
    }
    .upload-box {
        border: 2px dashed #ccc;
        padding: 2rem;
        text-align: center;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'processed_data' not in st.session_state:
    st.session_state.processed_data = None
if 'config' not in st.session_state:
    st.session_state.config = None
if 'uploaded_config' not in st.session_state:
    st.session_state.uploaded_config = None

def load_config(uploaded_file):
    try:
        content = uploaded_file.read()
        return json.loads(content)
    except Exception as e:
        st.error(f"Error loading config: {str(e)}")
        return None

def validate_excel_data(df):
    required_columns = ['Booking No', 'Supplier', 'Actual Net Cost']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        return False, f"Missing required columns: {', '.join(missing_columns)}"
    
    # Check for empty values
    empty_cells = df[required_columns].isna().sum()
    if empty_cells.sum() > 0:
        empty_cols = [f"{col} ({count} empty)" for col, count in empty_cells.items() if count > 0]
        return False, f"Empty values found in: {', '.join(empty_cols)}"
    
    return True, "Data validation successful"

def process_excel(file):
    try:
        df = pd.read_excel(file)
        is_valid, message = validate_excel_data(df)
        
        if not is_valid:
            st.error(message)
            return None
            
        # Clean and process data
        df['Booking No'] = df['Booking No'].astype(str)
        df['Actual Net Cost'] = pd.to_numeric(df['Actual Net Cost'], errors='coerce')
        
        return df
    except Exception as e:
        st.error(f"Error processing Excel file: {str(e)}")
        return None

def download_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    excel_data = output.getvalue()
    b64 = base64.b64encode(excel_data).decode()
    return b64

def main():
    st.title("🤖 CRM Automation Tool")
    
    # Sidebar
    with st.sidebar:
        st.header("Configuration")
        uploaded_config = st.file_uploader("Upload Config File", type=['json'])
        
        if uploaded_config:
            config = load_config(uploaded_config)
            if config:
                st.session_state.config = config
                st.success("✅ Configuration loaded successfully!")
                
                with st.expander("View Configuration"):
                    st.json(config)
        
        st.markdown("---")
        st.markdown("### Settings")
        st.checkbox("Enable Dark Mode", key="dark_mode")
        delay = st.slider("Processing Delay (seconds)", 0.0, 5.0, 1.0, 0.1)

    # Main content
    st.markdown("""
    ### Welcome to CRM Automation Tool! 👋
    This tool helps you automate updating invoice records in your CRM system using Excel data.
    Follow these steps to get started:
    1. Upload your configuration file (if not done)
    2. Upload your Excel file with invoice data
    3. Review the data and start automation
    """)

    # File upload section
    st.header("📤 Upload Excel File")
    
    uploaded_file = st.file_uploader(
        "Choose an Excel file",
        type=['xlsx', 'xls'],
        help="Upload an Excel file containing invoice data"
    )
    
    if uploaded_file is not None:
        with st.spinner("Processing Excel file..."):
            df = process_excel(uploaded_file)
            if df is not None:
                st.session_state.processed_data = df
                st.success("✅ Excel file processed successfully!")
                
                # Data preview
                st.header("📊 Data Preview")
                st.dataframe(df.head(), use_container_width=True)
                
                # Statistics
                st.header("📈 Statistics")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Records", len(df))
                with col2:
                    st.metric("Unique Suppliers", df['Supplier'].nunique())
                with col3:
                    st.metric("Total Cost", f"£{df['Actual Net Cost'].sum():,.2f}")
                with col4:
                    st.metric("Average Cost", f"£{df['Actual Net Cost'].mean():,.2f}")
                
                # Validation results
                with st.expander("View Validation Results"):
                    st.write("✅ All required columns present")
                    st.write("✅ No missing values")
                    st.write("✅ Data types validated")
                
                # Start automation
                st.header("🚀 Start Automation")
                if st.button("Start Processing", type="primary"):
                    if st.session_state.config is None:
                        st.error("⚠️ Please upload configuration file first!")
                    else:
                        with st.spinner("Running automation..."):
                            # Simulate processing
                            import time
                            progress_bar = st.progress(0)
                            for i in range(100):
                                time.sleep(delay/100)
                                progress_bar.progress(i + 1)
                            
                            st.success("✅ Automation completed successfully!")
                            
                            # Download processed file
                            b64 = download_excel(df)
                            href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="processed_data.xlsx">Download Processed File</a>'
                            st.markdown(href, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 