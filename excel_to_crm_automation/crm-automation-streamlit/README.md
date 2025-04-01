# CRM Automation Tool - Streamlit Version

A modern web interface for automating CRM updates using Excel data, built with Streamlit.

## Features

- 🌐 Web-based interface
- 📊 Excel file upload and validation
- 📈 Real-time data preview and statistics
- ⚙️ Configuration management
- 🚀 No local installation required
- 💻 Works on any device with a web browser

## Quick Start

1. Visit the app at: [Your Streamlit App URL]
2. Upload your configuration file (JSON)
3. Upload your Excel file
4. Review the data
5. Start the automation

## Excel File Format

Your Excel file should contain these columns:
- **Booking No**: Invoice number
- **Supplier**: Supplier name
- **Actual Net Cost**: The cost to update

## Local Development

If you want to run the app locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run streamlit_app.py
```

## Configuration

The tool uses a `config.json` file for CRM settings. You can:
1. Upload an existing config file
2. Edit the configuration in the web interface
3. Save changes to the configuration

## Security

- No sensitive data is stored
- All processing happens in memory
- Secure file handling
- CORS and XSRF protection enabled

## Support

For issues or questions, please create an issue in the repository. 