"""
Configuration Manager Module

This module handles loading and accessing configuration settings.
"""

import logging
import os
import configparser

class ConfigManager:
    def __init__(self, config_path):
        """
        Initialize the configuration manager
        
        Args:
            config_path: Path to the configuration file
        """
        self.config_path = config_path
        self.config = configparser.ConfigParser()
        
        # Load configuration
        self._load_config()
    
    def _load_config(self):
        """Load configuration from file"""
        try:
            # Check if config file exists
            if os.path.exists(self.config_path):
                logging.info(f"Loading configuration from: {self.config_path}")
                self.config.read(self.config_path)
            else:
                logging.warning(f"Configuration file not found: {self.config_path}")
                # Create with default values
                self._create_default_config()
        except Exception as e:
            logging.error(f"Error loading configuration: {str(e)}")
            # Create with default values as fallback
            self._create_default_config()
    
    def _create_default_config(self):
        """Create a default configuration file"""
        try:
            logging.info(f"Creating default configuration at: {self.config_path}")
            
            # General section
            self.config['General'] = {
                'check_interval_seconds': '30',
                'error_retry_seconds': '60',
                'temp_dir': 'temp',
                'log_level': 'INFO'
            }
            
            # WhatsApp section
            self.config['WhatsApp'] = {
                'group_name': 'Payment Confirmation Group',
                'whatsapp_window_title': 'WhatsApp',
                'message_check_interval': '5',
                'verification_timeout': '3600',
                'verification_keywords': 'received, confirmed, approved'
            }
            
            # OCR section
            self.config['OCR'] = {
                'tesseract_path': 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe',
                'language': 'eng',
                'invoice_number_regex': '[Ii]nvoice\\s*#?\\s*(\\w+)',
                'amount_regex': '(?:USD|£|₹|€|Rs\\.?|INR|$)?\\s*(\\d+(?:[,.]\\d+)?)',
                'date_regex': '(\\d{1,2}[-/\\.]\\d{1,2}[-/\\.]\\d{2,4})'
            }
            
            # CRM section
            self.config['CRM'] = {
                'crm_window_title': 'CRM System',
                'search_button_x': '500',
                'search_button_y': '300',
                'payment_field_x': '600',
                'payment_field_y': '400',
                'save_button_x': '700',
                'save_button_y': '500',
                'download_button_x': '750',
                'download_button_y': '550',
                'action_delay': '1.5'
            }
            
            # Email section
            self.config['Email'] = {
                'email_client_title': 'Outlook',
                'compose_button_x': '800',
                'compose_button_y': '600',
                'to_field_x': '850',
                'to_field_y': '650',
                'subject_field_x': '850',
                'subject_field_y': '680',
                'body_field_x': '850',
                'body_field_y': '720',
                'attach_button_x': '920',
                'attach_button_y': '780',
                'send_button_x': '900',
                'send_button_y': '700',
                'subject_template': 'Payment Confirmation: Invoice #{invoice_number}',
                'email_template_path': 'templates/payment_confirmation_email.txt'
            }
            
            # Write to file
            with open(self.config_path, 'w') as configfile:
                self.config.write(configfile)
            
            logging.info("Default configuration created")
        except Exception as e:
            logging.error(f"Error creating default configuration: {str(e)}")
    
    def get(self, section, key, default=None):
        """
        Get a configuration value as string
        
        Args:
            section: Configuration section
            key: Configuration key
            default: Default value if section/key doesn't exist
            
        Returns:
            Configuration value as string
        """
        try:
            if section in self.config and key in self.config[section]:
                return self.config[section][key]
            return default
        except Exception as e:
            logging.error(f"Error getting config value [{section}][{key}]: {str(e)}")
            return default
    
    def get_int(self, section, key, default=0):
        """
        Get a configuration value as integer
        
        Args:
            section: Configuration section
            key: Configuration key
            default: Default value if section/key doesn't exist
            
        Returns:
            Configuration value as integer
        """
        try:
            value = self.get(section, key)
            if value is not None:
                return int(value)
            return default
        except (ValueError, TypeError):
            logging.warning(f"Could not convert [{section}][{key}] to integer, using default: {default}")
            return default
    
    def get_float(self, section, key, default=0.0):
        """
        Get a configuration value as float
        
        Args:
            section: Configuration section
            key: Configuration key
            default: Default value if section/key doesn't exist
            
        Returns:
            Configuration value as float
        """
        try:
            value = self.get(section, key)
            if value is not None:
                return float(value)
            return default
        except (ValueError, TypeError):
            logging.warning(f"Could not convert [{section}][{key}] to float, using default: {default}")
            return default
    
    def get_boolean(self, section, key, default=False):
        """
        Get a configuration value as boolean
        
        Args:
            section: Configuration section
            key: Configuration key
            default: Default value if section/key doesn't exist
            
        Returns:
            Configuration value as boolean
        """
        try:
            value = self.get(section, key)
            if value is not None:
                return value.lower() in ('true', 'yes', '1', 'on')
            return default
        except Exception:
            logging.warning(f"Could not convert [{section}][{key}] to boolean, using default: {default}")
            return default
    
    def set(self, section, key, value):
        """
        Set a configuration value
        
        Args:
            section: Configuration section
            key: Configuration key
            value: Value to set
            
        Returns:
            Boolean indicating if successful
        """
        try:
            # Create section if it doesn't exist
            if section not in self.config:
                self.config[section] = {}
            
            # Set value
            self.config[section][key] = str(value)
            
            # Write to file
            with open(self.config_path, 'w') as configfile:
                self.config.write(configfile)
            
            return True
        except Exception as e:
            logging.error(f"Error setting config value [{section}][{key}]: {str(e)}")
            return False
