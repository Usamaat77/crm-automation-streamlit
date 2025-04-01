"""
CRM Automator Module

This module handles the automation of updating the CRM system with data from Excel.
"""
import os
import time
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from browser_controller import BrowserController


class CRMAutomator:
    def __init__(self, config=None):
        """
        Initialize the CRM automator with configuration
        
        Args:
            config: Dictionary containing configuration options
        """
        self.config = config or {}
        self.browser = BrowserController(config)
        self.logger = logging.getLogger(__name__)
        
        # Get CRM configuration
        crm_config = self.config.get('crm', {})
        self.crm_url = crm_config.get('url', '')
        self.field_mappings = crm_config.get('field_mappings', {})
        
    def start(self, headless=False):
        """
        Start the browser for CRM automation
        
        Args:
            headless: Boolean indicating if browser should run in headless mode
            
        Returns:
            Boolean indicating if browser was started successfully
        """
        return self.browser.start_browser(headless)
    
    def login_to_crm(self, username, password):
        """
        Login to the CRM system
        
        Args:
            username: Username for CRM login
            password: Password for CRM login
            
        Returns:
            Boolean indicating if login was successful
        """
        try:
            # Get login configuration
            crm_config = self.config.get('crm', {})
            login_config = crm_config.get('login', {})
            
            # Check if the URL is set
            if not self.crm_url:
                self.logger.error("CRM URL is not set")
                return False
                
            # Navigate to login page
            if not self.browser.navigate_to(self.crm_url):
                self.logger.error(f"Failed to navigate to login page at {self.crm_url}")
                return False
                
            # Get field locators
            username_field = login_config.get('username_field', {})
            password_field = login_config.get('password_field', {})
            login_button = login_config.get('login_button', {})
            
            # Check if field locators are properly set
            if not username_field or not password_field or not login_button:
                self.logger.error("Login field locators are incomplete")
                return False
                
            # Wait for the page to load
            time.sleep(2)
            
            # Enter username
            username_locator_type = getattr(By, username_field.get('type', 'XPATH').upper())
            if not self.browser.input_text(
                username_locator_type,
                username_field.get('value', ''),
                username,
                clear_first=True
            ):
                self.logger.error("Failed to input username")
                return False
                
            # Enter password
            password_locator_type = getattr(By, password_field.get('type', 'XPATH').upper())
            if not self.browser.input_text(
                password_locator_type,
                password_field.get('value', ''),
                password,
                clear_first=True
            ):
                self.logger.error("Failed to input password")
                return False
                
            # Click login button
            login_button_type = getattr(By, login_button.get('type', 'XPATH').upper())
            if not self.browser.click_element(
                login_button_type,
                login_button.get('value', '')
            ):
                self.logger.error("Failed to click login button")
                return False
                
            # Wait for the dashboard to load
            time.sleep(5)
            
            # Check if login was successful
            if "login" in self.browser.driver.current_url.lower():
                self.logger.error("Login failed, still on login page")
                return False
                
            self.logger.info("Successfully logged in to CRM")
            return True
            
        except Exception as e:
            self.logger.error(f"Error during login: {str(e)}")
            return False
    
    def navigate_to_crm_module(self):
        """
        Navigate to the CRM module from the dashboard
        
        Returns:
            Boolean indicating if navigation was successful
        """
        try:
            # Get navigation configuration
            crm_config = self.config.get('crm', {})
            nav_config = crm_config.get('navigation', {})
            
            # Get CRM module locator
            crm_module = nav_config.get('crm_module', {})
            if not crm_module:
                self.logger.error("CRM module locator is not configured")
                return False
                
            # Click on CRM module
            crm_module_type = getattr(By, crm_module.get('type', 'XPATH').upper())
            if not self.browser.click_element(
                crm_module_type,
                crm_module.get('value', '')
            ):
                self.logger.error("Failed to click on CRM module")
                return False
                
            # Wait for the CRM page to load
            time.sleep(3)
            
            # Check if we need to navigate to booking list
            booking_list = nav_config.get('booking_list', {})
            if booking_list:
                booking_list_type = getattr(By, booking_list.get('type', 'XPATH').upper())
                if not self.browser.click_element(
                    booking_list_type,
                    booking_list.get('value', '')
                ):
                    self.logger.error("Failed to click on Booking List")
                    return False
                    
                # Wait for booking list to load
                time.sleep(3)
                
            return True
            
        except Exception as e:
            self.logger.error(f"Error navigating to CRM module: {str(e)}")
            return False
    
    def navigate_to_crm(self):
        """
        Navigate to the CRM URL
        
        Returns:
            Boolean indicating if navigation was successful
        """
        if not self.crm_url:
            self.logger.error("CRM URL is not set")
            return False
            
        return self.browser.navigate_to(self.crm_url)
    
    def search_invoice(self, invoice_number):
        """
        Search for an invoice in the CRM system
        
        Args:
            invoice_number: The invoice number to search for (without "SZ" prefix)
            
        Returns:
            Boolean indicating if search was successful
        """
        # Get field mappings from config
        crm_config = self.config.get('crm', {})
        field_mappings = crm_config.get('field_mappings', {})
        
        # Get invoice number search field and search button
        search_field_locator = field_mappings.get('invoice_number_search', {})
        search_button_locator = field_mappings.get('search_button', {})
        
        # Check if search configuration is properly set
        if not search_field_locator or not search_button_locator:
            self.logger.error("Search configuration is incomplete")
            return False
            
        # Extract numeric part if invoice number starts with SZ
        if invoice_number.upper().startswith('SZ'):
            invoice_number = invoice_number[2:].strip()
        
        self.logger.info(f"Searching for invoice number: {invoice_number}")
        
        # Take a screenshot before search
        screenshot_path = f"screenshots/before_search_{invoice_number}_{int(time.time())}.png"
        self.browser.take_screenshot(screenshot_path)
        
        # Input the invoice number in the search field
        locator_type = getattr(By, search_field_locator.get('type', 'XPATH').upper())
        if not self.browser.input_text(
            locator_type, 
            search_field_locator.get('value'), 
            invoice_number,
            clear_first=True
        ):
            self.logger.error("Failed to input invoice number in search field")
            return False
            
        # Click the search button
        locator_type = getattr(By, search_button_locator.get('type', 'XPATH').upper())
        if not self.browser.click_element(
            locator_type, 
            search_button_locator.get('value'), 
            wait_time=2
        ):
            self.logger.error("Failed to click search button")
            return False
            
        # Give a moment for the results to load fully
        time.sleep(3)
        
        # Take a screenshot after search
        screenshot_path = f"screenshots/after_search_{invoice_number}_{int(time.time())}.png"
        self.browser.take_screenshot(screenshot_path)
        
        # Try to find the booking row to make sure it exists
        invoice_row_locator = field_mappings.get('invoice_row', {})
        if invoice_row_locator:
            row_locator_type = getattr(By, invoice_row_locator.get('type', 'XPATH').upper())
            row_locator_value = invoice_row_locator.get('value', '').replace('{invoice_number}', invoice_number)
            
            if not self.browser.wait_for_element(
                row_locator_type, 
                row_locator_value,
                timeout=5
            ):
                self.logger.error(f"Invoice row not found for number: {invoice_number}")
                
                # Take a screenshot of the search results
                screenshot_path = f"screenshots/search_results_not_found_{invoice_number}_{int(time.time())}.png"
                self.browser.take_screenshot(screenshot_path)
                self.logger.info(f"Saved search results screenshot to {screenshot_path}")
                
                return False
                
        return True
    
    def open_invoice_for_editing(self, invoice_row_identifier):
        """
        Open an invoice for editing in the CRM system
        
        Args:
            invoice_row_identifier: Identifier for the invoice row (booking number without "SZ" prefix)
            
        Returns:
            Boolean indicating if opening was successful
        """
        # Get field mappings from config
        crm_config = self.config.get('crm', {})
        field_mappings = crm_config.get('field_mappings', {})
        
        # Get locators from field mappings
        invoice_row_locator = field_mappings.get('invoice_row', {})
        add_actual_net_button_locator = field_mappings.get('add_actual_net_button', {})
        
        # Check if edit configuration is properly set
        if not invoice_row_locator or not add_actual_net_button_locator:
            self.logger.error("Edit configuration is incomplete")
            return False
        
        # Take a screenshot before clicking the invoice row
        screenshot_path = f"screenshots/before_open_invoice_{invoice_row_identifier}_{int(time.time())}.png"
        self.browser.take_screenshot(screenshot_path)
            
        # Find and click the invoice row (booking link)
        # The row should already be found during the search_invoice call
        # but we'll try to click on it directly here
        row_locator_type = getattr(By, invoice_row_locator.get('type', 'XPATH').upper())
        row_locator_value = invoice_row_locator.get('value', '')
        
        # Replace the placeholder with the actual identifier
        row_locator_value = row_locator_value.replace('{invoice_number}', invoice_row_identifier)
        
        self.logger.info(f"Looking for invoice row with: {row_locator_value}")
        
        # Wait for the invoice row to be visible and click it
        if not self.browser.click_element(
            row_locator_type, 
            row_locator_value, 
            wait_time=3
        ):
            self.logger.error(f"Invoice row not found: {invoice_row_identifier}")
            return False
        
        # Wait for the page to load after clicking the invoice
        time.sleep(5)
        
        # Take a screenshot after opening the booking details
        screenshot_path = f"screenshots/after_open_invoice_{invoice_row_identifier}_{int(time.time())}.png"
        self.browser.take_screenshot(screenshot_path)
        
        # Click the Add Actual Net button
        add_net_button_type = getattr(By, add_actual_net_button_locator.get('type', 'XPATH').upper())
        if not self.browser.click_element(
            add_net_button_type, 
            add_actual_net_button_locator.get('value'), 
            wait_time=3
        ):
            self.logger.error("Add Actual Net button not found")
            
            # Take a screenshot if button not found
            screenshot_path = f"screenshots/add_net_button_not_found_{int(time.time())}.png"
            self.browser.take_screenshot(screenshot_path)
            
            return False
        
        # Wait for form fields to load after clicking Add Actual Net button
        time.sleep(2)
        
        # Take a screenshot after clicking Add Actual Net button
        screenshot_path = f"screenshots/after_click_add_net_{invoice_row_identifier}_{int(time.time())}.png"
        self.browser.take_screenshot(screenshot_path)
        
        return True
    
    def update_field(self, field_key, field_value):
        """
        Update a specific field in the invoice form
        
        Args:
            field_key: Key of the field in the field_mappings configuration
            field_value: Value to set in the field
            
        Returns:
            Boolean indicating if update was successful
        """
        # Get field mappings from config
        crm_config = self.config.get('crm', {})
        field_mappings = crm_config.get('field_mappings', {})
        
        if field_key not in field_mappings:
            self.logger.error(f"Field mapping not found for: {field_key}")
            return False
            
        field_config = field_mappings[field_key]
        field_locator_type = getattr(By, field_config.get('type', 'NAME').upper())
        field_locator_value = field_config.get('value')
        
        # Check if the field configuration is valid
        if not field_locator_value:
            self.logger.error(f"Invalid field configuration for: {field_key}")
            return False
        
        # Take a screenshot before updating the field
        screenshot_path = f"screenshots/before_update_{field_key}_{int(time.time())}.png"
        self.browser.take_screenshot(screenshot_path)
            
        # For simplicity, assume all fields are text input fields
        # You can extend this to handle dropdowns, checkboxes, etc.
        if not self.browser.input_text(
            field_locator_type, 
            field_locator_value, 
            str(field_value),
            clear_first=True
        ):
            self.logger.error(f"Failed to input value into field: {field_key}")
            return False
        
        # Take a screenshot after updating the field
        screenshot_path = f"screenshots/after_update_{field_key}_{int(time.time())}.png"
        self.browser.take_screenshot(screenshot_path)
            
        return True
    
    def save_changes(self):
        """
        Save the changes made to the invoice by clicking the Save button
        
        Returns:
            Boolean indicating if save was successful
        """
        # Get field mappings from config
        crm_config = self.config.get('crm', {})
        field_mappings = crm_config.get('field_mappings', {})
        
        # Get save button locator from field mappings
        save_button_locator = field_mappings.get('save_button', {})
        
        # Check if save configuration is properly set
        if not save_button_locator:
            self.logger.error("Save button configuration is incomplete")
            return False
        
        # Give a moment for fields to be properly set
        time.sleep(1)
        
        # Take a screenshot before saving
        screenshot_path = f"screenshots/before_save_{int(time.time())}.png"
        self.browser.take_screenshot(screenshot_path)
        self.logger.info(f"Saved pre-save screenshot to {screenshot_path}")
            
        # Click the save button
        save_button_locator_type = getattr(By, save_button_locator.get('type', 'XPATH').upper())
        if not self.browser.click_element(
            save_button_locator_type, 
            save_button_locator.get('value'), 
            wait_time=3
        ):
            self.logger.error("Failed to click save button")
            return False
        
        # Give a moment for the save to process
        time.sleep(2)
                
        # Take a screenshot after saving
        screenshot_path = f"screenshots/after_save_{int(time.time())}.png"
        self.browser.take_screenshot(screenshot_path)
        self.logger.info(f"Saved post-save screenshot to {screenshot_path}")
        
        return True
    
    def update_invoice(self, invoice_identifier, invoice_data, username=None, password=None, max_retries=3):
        """
        Update an invoice in the CRM system
        
        Args:
            invoice_identifier: The invoice identifier (usually invoice number)
            invoice_data: Dictionary with invoice data
            username: Optional username for re-login if needed
            password: Optional password for re-login if needed
            max_retries: Maximum number of retry attempts
            
        Returns:
            Boolean indicating if update was successful
        """
        if not self.browser.driver:
            self.logger.error("Browser not initialized")
            return False
            
        retry_count = 0
        while retry_count < max_retries:
            try:
                # Check if we're on the right page
                if "booking-list" not in self.browser.driver.current_url.lower():
                    # Try to navigate to CRM module
                    self.logger.info("Not on booking list page, attempting to navigate")
                    if not self.navigate_to_crm_module():
                        # Try to navigate to CRM directly
                        self.navigate_to_crm()
                        
                        # If we have credentials, try to login
                        if username and password:
                            self.login_to_crm(username, password)
                            self.navigate_to_crm_module()
                
                # Search for the invoice
                self.logger.info(f"Searching for invoice: {invoice_identifier}")
                if not self.search_invoice(invoice_identifier):
                    self.logger.error(f"Invoice not found: {invoice_identifier}")
                    return False
                    
                # Wait a moment for the page to update
                time.sleep(2)
                
                # Extract the row identifier from the invoice data
                row_identifier = f"SZ{invoice_identifier}"
                
                # Open invoice for editing
                self.logger.info(f"Opening invoice for editing: {row_identifier}")
                if not self.open_invoice_for_editing(row_identifier):
                    self.logger.error(f"Failed to open invoice for editing: {row_identifier}")
                    return False
                    
                # Update each field
                update_success = True
                
                # Update supplier field
                supplier = invoice_data.get('supplier', '')
                if supplier:
                    self.logger.info(f"Updating supplier: {supplier}")
                    if not self.update_field('supplier', supplier):
                        self.logger.error(f"Failed to update supplier field")
                        update_success = False
                        
                # Update actual net cost field
                actual_net_cost = invoice_data.get('actual_net_cost', '')
                if actual_net_cost:
                    self.logger.info(f"Updating actual net cost: {actual_net_cost}")
                    if not self.update_field('actual_net_cost', actual_net_cost):
                        self.logger.error(f"Failed to update actual net cost field")
                        update_success = False
                        
                # Save changes
                if update_success:
                    self.logger.info("Saving changes")
                    if not self.save_changes():
                        self.logger.error("Failed to save changes")
                        return False
                        
                    self.logger.info(f"Successfully updated invoice: {invoice_identifier}")
                    return True
                else:
                    self.logger.error("One or more fields could not be updated, not saving")
                    return False
                    
            except Exception as e:
                self.logger.error(f"Error updating invoice: {str(e)}")
                retry_count += 1
                
                if retry_count < max_retries:
                    self.logger.info(f"Retrying ({retry_count}/{max_retries})...")
                    time.sleep(5)  # Wait before retrying
                    
                    # If we have credentials, try to re-login
                    if username and password:
                        self.logger.info("Attempting to re-login")
                        self.navigate_to_crm()
                        self.login_to_crm(username, password)
                else:
                    self.logger.error(f"Failed to update invoice after {max_retries} attempts")
                    return False
                    
        return False
    
    def update_multiple_invoices(self, invoice_data_list, username=None, password=None):
        """
        Update multiple invoices with their respective data
        
        Args:
            invoice_data_list: List of dictionaries, each containing invoice identifier and data
            username: Optional username for CRM login (if not provided, will need to be logged in already)
            password: Optional password for CRM login
            
        Returns:
            Dictionary with results for each invoice
        """
        results = {}
        
        # Login to the CRM system if credentials are provided
        if username and password:
            if not self.login_to_crm(username, password):
                self.logger.error("Failed to log in to CRM")
                return {"error": "Login failed"}
                
            # Navigate to CRM module and booking list
            if not self.navigate_to_crm_module():
                self.logger.error("Failed to navigate to CRM module")
                return {"error": "Navigation to CRM module failed"}
                
        # Process each invoice
        for invoice_data in invoice_data_list:
            invoice_identifier = invoice_data.get('invoice_number')
            if not invoice_identifier:
                self.logger.error("Invoice identifier not found in data")
                continue
                
            # Remove the identifier from the data to update
            update_data = {k: v for k, v in invoice_data.items() if k != 'invoice_number'}
            
            # Update the invoice (don't need to login again for each invoice)
            success = self.update_invoice(invoice_identifier, update_data)
            
            # Store the result
            results[invoice_identifier] = {
                'success': success,
                'timestamp': time.time()
            }
            
        return results
    
    def close(self):
        """Close the browser session"""
        self.browser.close()