import os
import sys
import uuid
import base64
import threading
import time
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

# Global dictionary to store task progress
# Format: { task_id: { 'status': 'processing'|'completed'|'error', 'data': {...}, 'error': 'msg' } }
tasks = {}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_file_in_background(task_id, input_path, output_path, original_filename):
    try:
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

        output_filename = f"redacted_{original_filename}"
        
        tasks[task_id] = {
            'status': 'completed',
            'data': {
                'filename': output_filename,
                'original_filename': original_filename,
                'stats': stats,
                'file_data': encoded_file
            }
        }
    except Exception as e:
        tasks[task_id] = {
            'status': 'error',
            'error': str(e)
        }
    finally:
        # Clean up files from server to prevent PII leakage
        if os.path.exists(input_path):
            try:
                os.remove(input_path)
            except:
                pass
        if os.path.exists(output_path):
            try:
                os.remove(output_path)
            except:
                pass

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
    task_id = str(uuid.uuid4())
    original_filename = secure_filename(file.filename)
    input_path = os.path.join(UPLOAD_FOLDER, f"{task_id}_{original_filename}")
    output_filename = f"redacted_{original_filename}"
    output_path = os.path.join(OUTPUT_FOLDER, f"{task_id}_{output_filename}")

    try:
        file.save(input_path)
        
        # Initialize task status
        tasks[task_id] = {'status': 'processing'}
        
        # Start background thread
        thread = threading.Thread(
            target=process_file_in_background,
            args=(task_id, input_path, output_path, file.filename)
        )
        thread.daemon = True
        thread.start()

        # Return the task_id immediately so the browser doesn't timeout
        return jsonify({
            'success': True,
            'task_id': task_id
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/status/<task_id>', methods=['GET'])
def get_status(task_id):
    task = tasks.get(task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404
        
    if task['status'] == 'completed':
        # Send data and clean up memory
        data = task['data']
        del tasks[task_id]
        return jsonify({'status': 'completed', 'data': data})
        
    elif task['status'] == 'error':
        error = task['error']
        del tasks[task_id]
        return jsonify({'status': 'error', 'error': error})
        
    else:
        return jsonify({'status': 'processing'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
