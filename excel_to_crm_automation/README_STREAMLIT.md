# CRM Automation Tool - Streamlit Version

This is a user-friendly web interface for the CRM Automation Tool built with Streamlit. It allows you to upload Excel files and automate CRM updates without installing any dependencies locally.

## Features

- Web-based interface
- Excel file upload and validation
- Real-time data preview and statistics
- Configuration management
- No local installation required
- Works on any device with a web browser

## How to Run

### Option 1: Run on Streamlit Cloud (Recommended)

1. Go to [Streamlit Cloud](https://share.streamlit.io/)
2. Sign up or log in with your GitHub account
3. Click "New app"
4. Select this repository
5. Select `streamlit_app.py` as the main file
6. Click "Deploy"

### Option 2: Run Locally

If you want to run it locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run streamlit_app.py
```

## Usage

1. Open the web interface in your browser
2. Upload your `config.json` file in the sidebar (if needed)
3. Upload your Excel file with the following columns:
   - Booking No
   - Supplier
   - Actual Net Cost
4. Review the data preview and statistics
5. Click "Start Automation" to begin the process
6. Download the processed file when complete

## Excel File Format

Your Excel file should contain these columns:
- **Booking No**: Invoice number (with or without "SZ" prefix)
- **Supplier**: Name of the supplier as it appears in the CRM dropdown
- **Actual Net Cost**: The actual net cost to update in the CRM

## Configuration

The tool uses a `config.json` file for CRM settings. You can:
1. Upload an existing config file
2. Edit the configuration directly in the web interface
3. Save changes to the configuration

## Troubleshooting

- If the app doesn't load, try refreshing the page
- Make sure your Excel file has the correct column names
- Check the error messages in the interface for specific issues
- If you encounter any problems, try clearing your browser cache

## Security Note

This web interface is designed for internal use. When deploying to Streamlit Cloud, make sure to:
1. Set up proper authentication
2. Use secure credentials
3. Keep your config.json file secure

## Support

For any issues or questions, please refer to the main project documentation or create an issue in the repository. 