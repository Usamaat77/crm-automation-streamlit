import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import tempfile
from pathlib import Path

# Set page config
st.set_page_config(
    page_title="CRM Automation Tool",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state
if 'processed_data' not in st.session_state:
    st.session_state.processed_data = None
if 'config' not in st.session_state:
    st.session_state.config = None

def load_config():
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading config: {str(e)}")
        return None

def save_config(config):
    try:
        with open('config.json', 'w') as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        st.error(f"Error saving config: {str(e)}")

def process_excel(file, config):
    try:
        df = pd.read_excel(file)
        required_columns = ['Booking No', 'Supplier', 'Actual Net Cost']
        
        # Validate columns
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            st.error(f"Missing required columns: {', '.join(missing_columns)}")
            return None
            
        return df
    except Exception as e:
        st.error(f"Error processing Excel file: {str(e)}")
        return None

def main():
    st.title("🤖 CRM Automation Tool")
    st.markdown("""
    This tool helps you automate updating invoice records in your CRM system using Excel data.
    Upload your Excel file and configure the settings to get started.
    """)

    # Sidebar for configuration
    with st.sidebar:
        st.header("Configuration")
        
        # Load existing config
        if st.session_state.config is None:
            st.session_state.config = load_config()
        
        if st.session_state.config:
            st.success("Configuration loaded successfully!")
            
            # Display current settings
            st.subheader("Current Settings")
            st.json(st.session_state.config)
            
            # Allow editing config
            if st.button("Edit Configuration"):
                new_config = st.text_area("Edit JSON Configuration", 
                                        value=json.dumps(st.session_state.config, indent=2))
                try:
                    new_config = json.loads(new_config)
                    st.session_state.config = new_config
                    save_config(new_config)
                    st.success("Configuration updated!")
                except json.JSONDecodeError:
                    st.error("Invalid JSON format")
        else:
            st.warning("No configuration found. Please upload a config.json file.")

    # Main content area
    st.header("Upload Excel File")
    
    uploaded_file = st.file_uploader("Choose an Excel file", type=['xlsx', 'xls'])
    
    if uploaded_file is not None:
        # Process the Excel file
        if st.session_state.processed_data is None:
            st.session_state.processed_data = process_excel(uploaded_file, st.session_state.config)
        
        if st.session_state.processed_data is not None:
            st.success("Excel file processed successfully!")
            
            # Display preview
            st.subheader("Data Preview")
            st.dataframe(st.session_state.processed_data.head())
            
            # Show statistics
            st.subheader("Statistics")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Records", len(st.session_state.processed_data))
            with col2:
                st.metric("Unique Suppliers", st.session_state.processed_data['Supplier'].nunique())
            with col3:
                st.metric("Total Cost", f"£{st.session_state.processed_data['Actual Net Cost'].sum():,.2f}")
            
            # Start automation button
            if st.button("Start Automation", type="primary"):
                with st.spinner("Starting automation process..."):
                    # Create a temporary directory for processing
                    with tempfile.TemporaryDirectory() as temp_dir:
                        # Save the processed data
                        temp_excel = Path(temp_dir) / "processed_data.xlsx"
                        st.session_state.processed_data.to_excel(temp_excel, index=False)
                        
                        # Here you would integrate with your existing automation code
                        st.info("Automation process would start here...")
                        
                        # For now, we'll just show a success message
                        st.success("Automation completed successfully!")
                        
                        # Offer download of processed file
                        with open(temp_excel, "rb") as file:
                            st.download_button(
                                label="Download Processed File",
                                data=file,
                                file_name="processed_data.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )

if __name__ == "__main__":
    main() 