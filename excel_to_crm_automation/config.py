"""
Configuration Module

This module handles default configurations and user-specific configurations.
"""
import os
import json
import logging
from configparser import ConfigParser

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Default configuration for the specific CRM system
DEFAULT_CONFIG = {
    'browser': {
        'headless': False,
        'timeout': 15
    },
    'crm': {
        'url': 'https://mis.bestumrahpackagesuk.com/crm/booking-list',
        'search_invoice': {
            'search_field': {
                'type': 'XPATH',
                'value': '//input[@placeholder="Enter Booking Number"]'
            },
            'search_button': {
                'type': 'XPATH',
                'value': '//button[contains(text(), "Search")]'
            },
            'results_container': {
                'type': 'XPATH',
                'value': '//div[contains(@class, "booking-list")]'
            }
        },
        'edit_invoice': {
            'row_locator': {
                'type': 'XPATH',
                'value': '//div[contains(text(), "Booking #: SZ {identifier}")]'
            },
            'booking_link': {
                'type': 'XPATH',
                'value': '//div[contains(text(), "Booking #: SZ {identifier}")]'
            },
            'pnr_section': {
                'type': 'XPATH',
                'value': '//div[contains(text(), "PNR Details")]'
            },
            'add_actual_net_button': {
                'type': 'XPATH',
                'value': '//button[contains(text(), "Add Actual Net")]'
            },
            'popup_form': {
                'type': 'XPATH',
                'value': '//div[contains(text(), "Add / Update Flight Actual Net")]'
            }
        },
        'save_changes': {
            'save_button': {
                'type': 'XPATH',
                'value': '//button[contains(text(), "Save")]'
            },
            'close_button': {
                'type': 'XPATH',
                'value': '//button[contains(text(), "Close")]'
            },
            'success_indicator': {
                'type': 'XPATH',
                'value': '//div[contains(@class, "alert-success")]'
            }
        },
        'field_mappings': {
            'supplier': {
                'type': 'XPATH',
                'value': '//input[@placeholder="Supplier"]',
                'field_type': 'text'
            },
            'actual_net_cost': {
                'type': 'XPATH',
                'value': '//input[@placeholder="Net Cost"]',
                'field_type': 'text'
            }
        }
    },
    'excel': {
        'default_column_mapping': {
            'invoice_number': 'invoice_number',
            'supplier': 'supplier',
            'actual_net_cost': 'actual_net_cost'
        }
    }
}

class Config:
    def __init__(self, config_path='config.json'):
        """
        Initialize the configuration manager
        
        Args:
            config_path: Path to the configuration file
        """
        self.config_path = config_path
        self.config = DEFAULT_CONFIG.copy()
        self.load_config()
    
    def load_config(self):
        """
        Load configuration from file
        
        Returns:
            Boolean indicating if loading was successful
        """
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    user_config = json.load(f)
                    
                # Update the default config with user-specific settings
                self._update_config_recursive(self.config, user_config)
                logger.info(f"Configuration loaded from {self.config_path}")
                return True
            else:
                logger.warning(f"Configuration file not found at {self.config_path}, using defaults")
                self.save_config()  # Create a default config file
                return False
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}")
            return False
    
    def save_config(self):
        """
        Save configuration to file
        
        Returns:
            Boolean indicating if saving was successful
        """
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=4)
            logger.info(f"Configuration saved to {self.config_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving configuration: {str(e)}")
            return False
    
    def _update_config_recursive(self, target, source):
        """
        Recursively update a nested dictionary with values from another dictionary
        
        Args:
            target: Target dictionary to update
            source: Source dictionary with new values
        """
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._update_config_recursive(target[key], value)
            else:
                target[key] = value
    
    def get(self, section=None):
        """
        Get a section of the configuration or the entire configuration
        
        Args:
            section: Section name (optional)
            
        Returns:
            Dictionary with configuration
        """
        if section:
            path = section.split('.')
            result = self.config
            for key in path:
                if key in result:
                    result = result[key]
                else:
                    logger.warning(f"Configuration section not found: {section}")
                    return {}
            return result
        else:
            return self.config
    
    def set(self, section, value):
        """
        Set a configuration value
        
        Args:
            section: Section name (dot notation for nested sections)
            value: Value to set
            
        Returns:
            Boolean indicating if setting was successful
        """
        try:
            path = section.split('.')
            target = self.config
            
            # Navigate to the correct level
            for key in path[:-1]:
                if key not in target:
                    target[key] = {}
                target = target[key]
            
            # Set the value
            target[path[-1]] = value
            
            # Save the updated configuration
            return self.save_config()
        except Exception as e:
            logger.error(f"Error setting configuration: {str(e)}")
            return False
    
    def update_field_mapping(self, field_name, field_config):
        """
        Update a field mapping in the configuration
        
        Args:
            field_name: Name of the field in the CRM
            field_config: Configuration for the field (locator type, value, etc.)
            
        Returns:
            Boolean indicating if update was successful
        """
        try:
            if 'field_mappings' not in self.config['crm']:
                self.config['crm']['field_mappings'] = {}
                
            self.config['crm']['field_mappings'][field_name] = field_config
            return self.save_config()
        except Exception as e:
            logger.error(f"Error updating field mapping: {str(e)}")
            return False
    
    def update_column_mapping(self, column_mapping):
        """
        Update the Excel column mapping in the configuration
        
        Args:
            column_mapping: Dictionary mapping Excel column names to CRM field names
            
        Returns:
            Boolean indicating if update was successful
        """
        try:
            self.config['excel']['default_column_mapping'] = column_mapping
            return self.save_config()
        except Exception as e:
            logger.error(f"Error updating column mapping: {str(e)}")
            return False
    
    def set_crm_url(self, url):
        """
        Set the CRM URL in the configuration
        
        Args:
            url: URL of the CRM
            
        Returns:
            Boolean indicating if setting was successful
        """
        return self.set('crm.url', url)