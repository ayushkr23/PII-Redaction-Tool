import os
import sys
import uuid
import base64
from collections import Counter
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename

# Add src to path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from pii_redactor import PIIRedactor

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024  # 20 MB max upload
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'redacted'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/redact', methods=['POST'])
def redact():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Only .docx files are supported'}), 400

    # Save uploaded file with a unique ID to avoid collisions
    unique_id = str(uuid.uuid4())[:8]
    original_filename = secure_filename(file.filename)
    input_path = os.path.join(UPLOAD_FOLDER, f"{unique_id}_{original_filename}")
    output_filename = f"redacted_{original_filename}"
    output_path = os.path.join(OUTPUT_FOLDER, f"{unique_id}_{output_filename}")

    try:
        file.save(input_path)

        redactor = PIIRedactor()
        redactor.redact_document(input_path, output_path)

        # Read the file and convert to base64
        with open(output_path, "rb") as f:
            encoded_file = base64.b64encode(f.read()).decode('utf-8')
            
        # Map raw entity types to nice display names
        display_map = {
            "PERSON": "Names",
            "EMAIL_ADDRESS": "Emails",
            "PHONE_NUMBER": "Phones",
            "ORGANIZATION": "Companies",
            "ADDRESS": "Addresses",
            "US_SSN": "SSNs",
            "CREDIT_CARD": "Cards",
            "DATE_OF_BIRTH": "DOBs",
            "IP_ADDRESS": "IPs"
        }
        
        stats = {}
        if hasattr(redactor, 'stats'):
            for k, v in redactor.stats.items():
                nice_name = display_map.get(k, k)
                stats[nice_name] = v

        return jsonify({
            'success': True,
            'filename': output_filename,
            'original_filename': file.filename,
            'stats': stats,
            'file_data': encoded_file
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        # Clean up files from server to prevent PII leakage
        if os.path.exists(input_path):
            os.remove(input_path)
        if os.path.exists(output_path):
            os.remove(output_path)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
