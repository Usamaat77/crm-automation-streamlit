#!/usr/bin/env python3
"""
Excel to CRM Automation - Simple Web Interface

This script provides a simple web interface for testing the Excel to CRM automation tool.
"""

import os
import json
import logging
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "development_key")

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'xlsx', 'xls'}

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload size

def allowed_file(filename):
    """Check if file has an allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_config():
    """Load configuration from config.json"""
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading configuration: {str(e)}")
        return {}

def save_config(config):
    """Save configuration to config.json"""
    try:
        with open('config.json', 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving configuration: {str(e)}")
        return False

@app.route('/')
def index():
    """Home page route"""
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    """Handle file upload"""
    if request.method == 'POST':
        # Check if a file was uploaded
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
            
        file = request.files['file']
        
        # Check if file is selected
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
            
        # Check if file has allowed extension
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            # Save file path in session
            session['excel_file'] = file_path
            
            return redirect(url_for('excel_details'))
        else:
            flash('Invalid file type. Please upload an Excel file (.xlsx or .xls)')
            return redirect(request.url)
            
    return render_template('upload.html')

@app.route('/excel_details')
def excel_details():
    """Display Excel file details"""
    # Check if file path is in session
    if 'excel_file' not in session:
        flash('No Excel file selected')
        return redirect(url_for('upload_file'))
        
    file_path = session['excel_file']
    
    # Check if file exists
    if not os.path.exists(file_path):
        flash('Excel file not found')
        return redirect(url_for('upload_file'))
        
    try:
        from excel_processor import ExcelProcessor
        
        # Process Excel file to get column info
        processor = ExcelProcessor(file_path)
        columns = processor.get_column_names()
        row_count = processor.get_row_count()
        
        # Get sample data (first 5 rows)
        sample_data = []
        for i in range(min(5, row_count)):
            row = processor.data.iloc[i]
            sample_data.append({col: row[col] for col in columns})
        
        return render_template('excel_details.html', 
                              filename=os.path.basename(file_path),
                              columns=columns,
                              row_count=row_count,
                              sample_data=sample_data)
    except Exception as e:
        flash(f'Error processing Excel file: {str(e)}')
        return redirect(url_for('upload_file'))

@app.route('/map_columns', methods=['GET', 'POST'])
def map_columns():
    """Map Excel columns to CRM fields"""
    # Check if file path is in session
    if 'excel_file' not in session:
        flash('No Excel file selected')
        return redirect(url_for('upload_file'))
        
    file_path = session['excel_file']
    
    # Check if file exists
    if not os.path.exists(file_path):
        flash('Excel file not found')
        return redirect(url_for('upload_file'))
        
    try:
        from excel_processor import ExcelProcessor
        
        # Process Excel file to get column info
        processor = ExcelProcessor(file_path)
        columns = processor.get_column_names()
        
        if request.method == 'POST':
            # Get column mapping from form
            column_mapping = {}
            required_fields = ['invoice_number', 'supplier', 'actual_net_cost']
            missing_fields = []
            
            for crm_field in required_fields:
                excel_column = request.form.get(crm_field)
                if excel_column and excel_column in columns:
                    column_mapping[crm_field] = excel_column
                else:
                    missing_fields.append(crm_field)
            
            # Check if all required fields are mapped
            if missing_fields:
                flash(f'Please map all required fields: {", ".join(missing_fields)}')
                return render_template('map_columns.html', 
                                      columns=columns,
                                      default_mapping=column_mapping)
            
            # Save column mapping in session
            session['column_mapping'] = column_mapping
            
            # Also save mapping to config for future use
            try:
                config = load_config()
                if 'excel' not in config:
                    config['excel'] = {}
                config['excel']['column_mapping'] = column_mapping
                save_config(config)
            except Exception as e:
                logger.warning(f"Could not save column mapping to config: {str(e)}")
            
            return redirect(url_for('prepare_automation'))
        
        # Get default column mapping from config
        config = load_config()
        default_mapping = config.get('excel', {}).get('column_mapping', {})
        
        # If no mapping in config, use hardcoded defaults
        if not default_mapping:
            default_mapping = {
                'invoice_number': 'Booking No',
                'supplier': 'Supplier',
                'actual_net_cost': 'Actual Net Cost'
            }
        
        # Validate default mapping against available columns
        for crm_field, excel_column in list(default_mapping.items()):
            if excel_column not in columns:
                # Remove invalid mappings
                default_mapping[crm_field] = ''
        
        return render_template('map_columns.html', 
                              columns=columns,
                              default_mapping=default_mapping)
    except Exception as e:
        flash(f'Error mapping columns: {str(e)}')
        logger.error(f"Error in map_columns: {str(e)}", exc_info=True)
        return redirect(url_for('upload_file'))

@app.route('/prepare_automation', methods=['GET', 'POST'])
def prepare_automation():
    """Prepare automation settings"""
    # Check if required session data exists
    if 'excel_file' not in session or 'column_mapping' not in session:
        flash('Missing required information')
        return redirect(url_for('upload_file'))
        
    if request.method == 'POST':
        # Get automation settings from form
        automation_settings = {
            'headless': 'headless' in request.form,
            'delay': float(request.form.get('delay', 1.0))
        }
        
        # Save automation settings in session
        session['automation_settings'] = automation_settings
        
        # Generate and display command
        file_path = session['excel_file']
        column_mapping = session['column_mapping']
        
        command = f"python run.py --excel \"{file_path}\""
        
        if automation_settings['headless']:
            command += " --headless"
            
        command += f" --delay {automation_settings['delay']}"
        
        if column_mapping:
            command += f" --column-mapping '{json.dumps(column_mapping)}'"
            
        session['command'] = command
        
        return render_template('automation_ready.html', command=command)
        
    return render_template('prepare_automation.html')

@app.route('/config', methods=['GET', 'POST'])
def manage_config():
    """Manage CRM configuration"""
    config = load_config()
    
    if request.method == 'POST':
        # Update CRM URL
        crm_url = request.form.get('crm_url')
        if crm_url:
            if 'crm' not in config:
                config['crm'] = {}
            config['crm']['url'] = crm_url
        
        # Save updated configuration
        save_config(config)
        flash('Configuration updated successfully')
        
    return render_template('config.html', config=config)

@app.route('/downloads/<path:filename>')
def download_file(filename):
    """Download a file"""
    return send_from_directory(
        os.path.dirname(os.path.abspath(__file__)),
        filename,
        as_attachment=True
    )

# Generate the package and create a download link
@app.route('/generate-package')
def generate_package():
    """Generate the package and provide a download link"""
    try:
        print("Starting package creation")
        
        from create_download_package import create_zip_package
        
        output_path = 'excel_to_crm_automation.zip'
        success = create_zip_package(output_path)
        
        if success:
            print(f"Package created successfully: {output_path}")
            flash('Package created successfully. Click the download button below.')
            return render_template('download_ready.html', filename=output_path)
        else:
            print("Failed to create package")
            flash('Failed to create package')
            return redirect(url_for('index'))
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error in generate_package: {str(e)}\n{error_details}")
        flash(f'Error: {str(e)}')
        return redirect(url_for('index'))

# Download the generated package
@app.route('/download-file/<filename>')
def download_file_direct(filename):
    """Download a file directly"""
    try:
        print(f"Attempting to download file: {filename}")
        filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
        
        if os.path.exists(filepath):
            print(f"File exists: {filepath}")
            return send_from_directory(
                os.path.dirname(os.path.abspath(__file__)),
                filename,
                as_attachment=True
            )
        else:
            print(f"File not found: {filepath}")
            flash('File not found')
            return redirect(url_for('index'))
    except Exception as e:
        import traceback
        print(f"Error in download_file_direct: {str(e)}\n{traceback.format_exc()}")
        flash(f'Error: {str(e)}')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)