# Excel to CRM Automation Tool

This tool automates the process of updating invoice records in a CRM system based on data from Excel files.

## Features

- Process Excel files with invoice data
- Automatically update CRM system with extracted data
- Configure field mappings and browser settings
- Command-line and web interface options
- Retry logic with automatic recovery
- Robust error handling and validation
- Screenshot capture for debugging

## Requirements

- Python 3.8 or higher
- Google Chrome browser
- ChromeDriver (compatible with your Chrome version)

## Installation

1. Download or clone this repository
2. Install the required Python packages:

```bash
pip install -r requirements-local.txt
```

3. Configure the `config.json` file with your CRM details

## Configuration

The `config.json` file contains configuration for:

- CRM URL and field mappings
- Browser settings
- Default column mappings

### Sample Configuration

```json
{
  "crm": {
    "url": "https://your-crm-url.com/login",
    "login": {
      "username_field": {
        "type": "xpath",
        "value": "//input[@name='username']"
      },
      "password_field": {
        "type": "xpath", 
        "value": "//input[@name='password']"
      },
      "login_button": {
        "type": "xpath",
        "value": "//button[contains(text(), 'Sign In')]"
      }
    },
    "field_mappings": {
      "invoice_number_search": {
        "type": "xpath",
        "value": "//input[@placeholder='Enter Booking Number']"
      },
      "search_button": {
        "type": "xpath",
        "value": "//button[contains(@class, 'btn-info') and text()='Search']"
      }
    }
  }
}
```

## Usage

### Command-Line Interface

```bash
# Basic usage
python run.py --excel path/to/your/excel_file.xlsx

# Run in headless mode
python run.py --excel path/to/your/excel_file.xlsx --headless

# Use custom column mapping
python run.py --excel path/to/your/excel_file.xlsx --column-mapping '{"invoice_number": "Invoice No", "supplier": "Vendor", "actual_net_cost": "Cost"}'

# Set delay between actions
python run.py --excel path/to/your/excel_file.xlsx --delay 2.0
```

### Simplified CLI

For a simpler interface with better error handling:

```bash
python run_simple.py --excel path/to/your/excel_file.xlsx [--headless] [--delay 2.0]
```

### Web Interface

```bash
# Start the web interface
python simple_main.py
```

Then open your browser to `http://localhost:5000`

## Excel File Format

The Excel file should contain these columns:

- **Booking No**: Invoice number (with or without "SZ" prefix)
- **Supplier**: Name of the supplier as it appears in the CRM dropdown
- **Actual Net Cost**: The actual net cost to update in the CRM

## How It Works

1. The tool reads the Excel file and extracts the invoice data
2. It logs in to the CRM system with your credentials
3. Navigates to the Customer Relation Management System module
4. Opens the Booking List page
5. For each invoice:
   - Searches for the invoice number
   - Opens the invoice details
   - Clicks the "Add Actual Net" button
   - Updates the supplier and actual net cost
   - Saves the changes
   
## New Features

### Retry Logic
The tool now includes retry logic for automation operations, automatically recovering from common errors like disconnections or timeouts.

### Improved Error Handling
More robust error handling has been added throughout the application, with detailed logging for better troubleshooting.

### Screenshot Capture
The tool now captures screenshots at key points in the automation process, helping you troubleshoot issues more effectively.

### Headless Mode Improvements
Headless mode has been updated for compatibility with newer Chrome versions, allowing automation to run in the background.

### Fallback Options
The browser controller now includes fallback options for WebDriver initialization, improving compatibility across different systems.

### Data Validation
Enhanced data validation ensures that Excel data is properly processed before automation begins, preventing errors during execution.

## Authentication

The tool supports automatic login to the CRM system. You have two options:

### Option 1: Pass credentials directly (Command-Line)

```bash
python run.py --excel path/to/your/excel_file.xlsx --username your_username --password your_password
```

### Option 2: Test the login process first

You can test if the login process works with your credentials using the test script:

```bash
python test_crm_login.py your_username your_password
```

This will:
1. Open the browser
2. Attempt to log in to the CRM system
3. Navigate to the booking list page
4. Take a screenshot to verify success
5. Optionally test searching for an invoice number

## Customization

You can customize the field mappings in the `config.json` file to match your CRM system's structure. The web interface also allows you to save and update these mappings.

## Troubleshooting

- **Browser doesn't start**: Make sure Chrome and ChromeDriver are installed and properly configured
- **Chrome version issues**: The tool now automatically tries to find a compatible ChromeDriver version
- **Invoice not found**: Verify that the invoice number format matches what the CRM expects
- **Field not updated**: Check the field mappings in the config file
- **Automation errors**: Check the log files and screenshots in the screenshots directory

## License

This project is licensed under the MIT License - see the LICENSE file for details.