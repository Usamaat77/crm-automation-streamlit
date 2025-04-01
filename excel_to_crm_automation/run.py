#!/usr/bin/env python3
"""
Excel to CRM Automation CLI

This script provides a command-line interface for updating CRM records based on Excel data.
"""

import os
import sys
import json
import argparse
import logging
import traceback

from excel_processor import ExcelProcessor
from crm_automator import CRMAutomator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('automation.log')
    ]
)
logger = logging.getLogger(__name__)

def parse_arguments():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(description='Excel to CRM Automation Tool')
    
    parser.add_argument('--excel', '-e', required=True, help='Path to Excel file with invoice data')
    parser.add_argument('--headless', action='store_true', help='Run browser in headless mode')
    parser.add_argument('--column-mapping', help='Custom column mapping (JSON format)')
    parser.add_argument('--delay', type=float, default=1.0, help='Delay in seconds between actions (default: 1.0)')
    parser.add_argument('--username', help='Username for CRM login')
    parser.add_argument('--password', help='Password for CRM login')
    parser.add_argument('--no-login', action='store_true', help='Skip login (use if already logged in)')
    
    return parser.parse_args()

def load_config():
    """Load configuration from config.json"""
    config_path = 'config.json'
    
    if not os.path.exists(config_path):
        logger.error(f"Configuration file not found: {config_path}")
        sys.exit(1)
    
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading configuration: {str(e)}")
        sys.exit(1)

def load_column_mapping(args, config):
    """Load column mapping from arguments or default configuration"""
    if args.column_mapping:
        try:
            return json.loads(args.column_mapping)
        except json.JSONDecodeError:
            logger.error("Invalid JSON format for column mapping")
            sys.exit(1)
    
    # Default column mapping
    return {
        "invoice_number": "Booking No",
        "supplier": "Supplier",
        "actual_net_cost": "Actual Net Cost"
    }

def main():
    """Main function to run the automation"""
    args = parse_arguments()
    config = load_config()
    column_mapping = load_column_mapping(args, config)
    
    logger.info(f"Starting Excel to CRM Automation with file: {args.excel}")
    
    # Check if Excel file exists
    if not os.path.exists(args.excel):
        logger.error(f"Excel file not found: {args.excel}")
        sys.exit(1)
    
    try:
        # Process Excel file
        logger.info("Processing Excel file...")
        excel_processor = ExcelProcessor(args.excel)
        invoices_data = excel_processor.process_file(column_mapping)
        
        if not invoices_data:
            logger.error("No valid invoice data found in Excel file")
            sys.exit(1)
        
        logger.info(f"Found {len(invoices_data)} invoices to process")
        
        # Initialize CRM automator
        crm_config = config.get('crm', {})
        crm_automator = CRMAutomator(crm_config)
        
        # Start automation
        logger.info("Starting browser automation...")
        crm_automator.start(headless=args.headless)
        
        # Handle login if credentials provided
        if args.username and args.password and not args.no_login:
            logger.info(f"Logging in with username: {args.username}")
            if not crm_automator.login_to_crm(args.username, args.password):
                logger.error("Failed to log in to CRM. Check your credentials.")
                crm_automator.close()
                sys.exit(1)
                
            # Navigate to CRM module after login
            logger.info("Navigating to CRM module")
            if not crm_automator.navigate_to_crm_module():
                logger.error("Failed to navigate to CRM module after login")
                crm_automator.close()
                sys.exit(1)
        else:
            # If no login credentials, just navigate to CRM
            logger.info(f"Navigating to CRM: {crm_config.get('url')}")
            crm_automator.navigate_to_crm()
            
            if not args.no_login:
                logger.warning("No login credentials provided. You may need to log in manually.")
                input("Press Enter after logging in manually...")
        
        # Process each invoice
        successful = 0
        failed = 0
        
        for i, invoice_data in enumerate(invoices_data, 1):
            invoice_id = invoice_data.get('invoice_number', 'Unknown')
            logger.info(f"Processing invoice {i}/{len(invoices_data)}: {invoice_id}")
            
            try:
                # Update invoice in CRM, pass credentials again for re-login if needed
                result = crm_automator.update_invoice(
                    invoice_id, 
                    invoice_data,
                    username=args.username if not args.no_login else None,
                    password=args.password if not args.no_login else None
                )
                
                if result:
                    logger.info(f"Successfully updated invoice: {invoice_id}")
                    successful += 1
                else:
                    logger.error(f"Failed to update invoice: {invoice_id}")
                    failed += 1
            except Exception as e:
                logger.error(f"Error updating invoice {invoice_id}: {str(e)}")
                failed += 1
        
        # Close browser
        crm_automator.close()
        
        # Summary
        logger.info("Automation completed!")
        logger.info(f"Total invoices: {len(invoices_data)}")
        logger.info(f"Successfully updated: {successful}")
        logger.info(f"Failed: {failed}")
        
    except Exception as e:
        logger.error(f"Automation failed: {str(e)}")
        logger.debug(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()