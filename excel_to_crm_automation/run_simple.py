#!/usr/bin/env python3
"""
Excel to CRM Automation - Simple CLI

This script provides a simplified command-line interface for running the CRM automation.
"""

import os
import sys
import json
import argparse
import traceback
import logging

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

def parse_args():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(description='Excel to CRM Automation Tool')
    
    parser.add_argument('--excel', '-e', required=True, help='Path to Excel file')
    parser.add_argument('--headless', action='store_true', help='Run browser in headless mode')
    parser.add_argument('--delay', type=float, default=1.0, help='Delay in seconds between actions')
    
    return parser.parse_args()

def main():
    """Main function"""
    args = parse_args()
    
    # Check if Excel file exists
    if not os.path.exists(args.excel):
        logger.error(f"Excel file not found: {args.excel}")
        sys.exit(1)
    
    try:
        # Load configuration
        config_path = 'config.json'
        config = {}
        
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                logger.info(f"Configuration loaded from: {config_path}")
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON in configuration file: {config_path}")
                sys.exit(1)
            except Exception as e:
                logger.error(f"Error loading configuration: {str(e)}")
                sys.exit(1)
        else:
            logger.warning(f"Configuration file not found: {config_path}, using defaults")
            # Create minimal default config
            config = {
                "crm": {
                    "url": "https://mis.bestumrahpackagesuk.com/login"
                }
            }
        
        # Process Excel file
        logger.info(f"Processing Excel file: {args.excel}")
        excel_processor = ExcelProcessor(args.excel)
        
        # Get column mapping from config or use defaults
        column_mapping = config.get('excel', {}).get('column_mapping', {})
        if not column_mapping:
            logger.warning("No column mapping found in config, using defaults")
            column_mapping = {
                'invoice_number': 'Booking No',
                'supplier': 'Supplier',
                'actual_net_cost': 'Actual Net Cost'
            }
        
        # Get invoice data from Excel
        invoices = excel_processor.process_file(column_mapping)
        if not invoices:
            logger.error("No valid invoice data found in Excel file")
            sys.exit(1)
            
        logger.info(f"Found {len(invoices)} invoices to process")
        
        # Initialize CRM automator
        logger.info("Initializing CRM automator")
        crm_config = config.get('crm', {})
        if not crm_config.get('url'):
            logger.error("CRM URL not configured")
            sys.exit(1)
            
        crm_automator = CRMAutomator(config)
        
        # Start browser
        logger.info("Starting browser")
        if not crm_automator.start(headless=args.headless):
            logger.error("Failed to start browser")
            sys.exit(1)
        
        # Login to CRM (assuming user is already logged in)
        logger.info("Navigating to CRM")
        if not crm_automator.navigate_to_crm():
            logger.error("Failed to navigate to CRM")
            crm_automator.close()
            sys.exit(1)
            
        # Wait for user to login if needed
        input("Please login to the CRM system if needed, then press Enter to continue...")
        
        # Process each invoice
        success_count = 0
        error_count = 0
        
        for i, invoice in enumerate(invoices, 1):
            invoice_id = invoice.get('invoice_number', 'Unknown')
            logger.info(f"Processing invoice {i}/{len(invoices)}: {invoice_id}")
            
            try:
                # Update invoice in CRM
                result = crm_automator.update_invoice(invoice_id, invoice)
                
                if result:
                    logger.info(f"Successfully updated invoice: {invoice_id}")
                    success_count += 1
                else:
                    logger.error(f"Failed to update invoice: {invoice_id}")
                    error_count += 1
            except Exception as e:
                logger.error(f"Error updating invoice {invoice_id}: {str(e)}")
                logger.debug(traceback.format_exc())
                error_count += 1
        
        # Close browser
        logger.info("Closing browser")
        crm_automator.close()
        
        # Summary
        logger.info("="*50)
        logger.info("Automation completed!")
        logger.info(f"Total invoices:      {len(invoices)}")
        logger.info(f"Successfully updated: {success_count}")
        logger.info(f"Failed:              {error_count}")
        logger.info("="*50)
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        logger.debug(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()