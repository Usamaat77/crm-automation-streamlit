"""
Excel Processor Module

This module handles the extraction of data from Excel files for CRM updating.
"""
import os
import pandas as pd
import logging


class ExcelProcessor:
    def __init__(self, file_path=None):
        """
        Initialize the Excel processor
        
        Args:
            file_path: Optional path to the Excel file to load
        """
        self.data = None
        self.file_path = None
        self.column_mapping = {}
        
        if file_path:
            self.load_excel_file(file_path)

    def load_excel_file(self, file_path):
        """
        Load an Excel file and store its data
        
        Args:
            file_path: Path to the Excel file
            
        Returns:
            Boolean indicating if loading was successful
        """
        try:
            if not os.path.exists(file_path):
                return False
                
            # Try to load the file with pandas
            self.data = pd.read_excel(file_path)
            self.file_path = file_path
            return True
        except Exception as e:
            print(f"Error loading Excel file: {str(e)}")
            return False
            
    def get_column_names(self):
        """
        Get the column names from the loaded Excel file
        
        Returns:
            List of column names
        """
        if self.data is None:
            return []
            
        return list(self.data.columns)
        
    def set_column_mapping(self, mapping):
        """
        Set the mapping between Excel columns and CRM fields
        
        Args:
            mapping: Dictionary mapping Excel column names to CRM field names
            
        Returns:
            Boolean indicating if mapping was set successfully
        """
        if self.data is None:
            return False
            
        # Validate that all keys in mapping exist in the Excel file
        excel_columns = set(self.data.columns)
        mapping_columns = set(mapping.keys())
        
        if not mapping_columns.issubset(excel_columns):
            invalid_columns = mapping_columns - excel_columns
            print(f"Invalid columns in mapping: {invalid_columns}")
            return False
            
        self.column_mapping = mapping
        return True
        
    def get_row_data(self, row_index):
        """
        Get the data for a specific row
        
        Args:
            row_index: Index of the row to retrieve
            
        Returns:
            Dictionary with the row data, mapped to CRM field names
        """
        if self.data is None or row_index < 0 or row_index >= len(self.data):
            return {}
            
        row = self.data.iloc[row_index]
        result = {}
        
        # Apply the column mapping
        for excel_col, crm_field in self.column_mapping.items():
            result[crm_field] = row[excel_col]
            
        return result
        
    def get_all_rows(self):
        """
        Get all rows from the Excel file
        
        Returns:
            List of dictionaries, each containing the row data mapped to CRM field names
        """
        if self.data is None:
            return []
            
        result = []
        for i in range(len(self.data)):
            result.append(self.get_row_data(i))
            
        return result
        
    def get_row_count(self):
        """
        Get the number of rows in the Excel file
        
        Returns:
            Integer indicating the number of rows
        """
        if self.data is None:
            return 0
            
        return len(self.data)
        
    def process_file(self, column_mapping):
        """
        Process the Excel file with the given column mapping
        
        Args:
            column_mapping: Dictionary mapping CRM fields to Excel column names
                Example: {'invoice_number': 'Booking No', 'supplier': 'Supplier'}
                
        Returns:
            List of dictionaries, each containing data for one invoice
        """
        if self.data is None:
            logging.error("No Excel data loaded")
            return []
        
        # Validate input data    
        if not isinstance(column_mapping, dict) or not column_mapping:
            logging.error("Invalid column mapping: must be a non-empty dictionary")
            return []
            
        # Invert the mapping for our use (we need Excel -> CRM)
        excel_to_crm = {}
        missing_columns = []
        
        for crm_field, excel_col in column_mapping.items():
            if isinstance(excel_col, str) and excel_col in self.data.columns:
                excel_to_crm[excel_col] = crm_field
            else:
                missing_columns.append(excel_col)
        
        if missing_columns:
            logging.warning(f"Columns not found in Excel file: {missing_columns}")
            
        if not excel_to_crm:
            logging.error("No valid columns found in the mapping")
            return []
            
        # Set the mapping and get all rows
        self.set_column_mapping(excel_to_crm)
        rows = self.get_all_rows()
        
        # Process each row to normalize the data
        result = []
        for i, row in enumerate(rows):
            try:
                # Skip empty rows
                if not row:
                    continue
                    
                # Extract invoice number and handle SZ prefix
                invoice_number = row.get('invoice_number', '')
                if isinstance(invoice_number, str) and invoice_number.upper().startswith('SZ'):
                    invoice_number = invoice_number[2:]  # Remove 'SZ' prefix
                elif not isinstance(invoice_number, (str, int, float)):
                    logging.warning(f"Invalid invoice number in row {i+1}: {invoice_number}")
                    continue
                    
                row['invoice_number'] = str(invoice_number).strip()
                
                # Convert numeric values to strings and handle NaN values
                for key, value in row.items():
                    if pd.isna(value):
                        row[key] = ''
                    elif isinstance(value, (int, float)):
                        row[key] = str(value)
                    elif not isinstance(value, str):
                        # Convert any other type to string
                        row[key] = str(value)
                
                # Validate required fields
                if not row.get('invoice_number'):
                    logging.warning(f"Missing invoice number in row {i+1}, skipping")
                    continue
                    
                # Add the processed row
                result.append(row)
                
            except Exception as e:
                logging.error(f"Error processing row {i+1}: {str(e)}")
                continue
            
        return result