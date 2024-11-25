from flask import Flask, request, jsonify, render_template, send_from_directory, url_for
import os
import re
from werkzeug.utils import secure_filename
import time

app = Flask(__name__)

# Directories for uploaded and processed files
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
ALLOWED_EXTENSIONS = {'txt', 'pdf'}

# Maximum file size (16 MB)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

# allowed file types
def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# validate lines
def validate_line(line):
    """Validate a line based on format requirements."""
    reasons = []
    if ':' not in line:
        reasons.append("Missing colon `:`")
    if '=' not in line:
        reasons.append("Missing equals sign `=`")
    return reasons

# home page
@app.route('/')
def home():
    """index - home page"""
    return render_template('index.html')

# process file: Micro Service End Point
@app.route('/process', methods=['POST'])
def process_file():
    """
    Handle file uploads and processing, then return processed data as JSON.
    """
    # Validate the incoming request
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided.'}), 400
    if 'category' not in request.form or 'level' not in request.form:
        return jsonify({'error': 'Category and level are required.'}), 400

    file = request.files['file']
    category = request.form['category']
    level = request.form['level']

    if file.filename == '':
        return jsonify({'error': 'No file selected.'}), 400
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Only TXT and PDF are allowed.'}), 400

    # Save the uploaded file with a secure filename
    filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)

    try:
        # Process the file content
        processed_data, invalid_lines = process_content(file_path)

        # Generate filenames
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        processed_filename = f"{level}_{category}_{timestamp}.txt"
        processed_file_path = os.path.join(PROCESSED_FOLDER, processed_filename)

        # Save the processed file
        with open(processed_file_path, 'w', encoding='utf-8') as outfile:
            outfile.write(processed_data)

        # Handle invalid lines
        invalid_file_url = None
        invalid_filename = None
        if invalid_lines:
            invalid_filename = f"invalid_words_{level}_{category}_{timestamp}.txt"
            invalid_file_path = os.path.join(PROCESSED_FOLDER, invalid_filename)
            with open(invalid_file_path, 'w', encoding='utf-8') as invalid_file:
                for line in invalid_lines:
                    invalid_file.write(
                        f"Line {line['line_number']}: {line['line_content']} ({line['reason']})\n"
                    )
            invalid_file_url = url_for('download_file', filename=invalid_filename, _external=True)


        # Construct the response
        response = {
            "message": f"Partial Success: The file '{file.filename}' was processed as {category} and {level}, however, some line errors occurred." if invalid_lines else f"Success: File processed successfully as {category} - {level}.",
            "processed_file": processed_filename,
            "processed_file_url": url_for('download_file', filename=processed_filename, _external=True),
            "invalid_file": invalid_filename,
            "invalid_file_url": invalid_file_url
        }

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": f"Processing failed: {str(e)}"}), 500

    finally:
        # Clean up the uploaded file
        if os.path.exists(file_path):
            os.remove(file_path)


def process_content(file_path):
    """
    Process the uploaded file content.
    Returns the processed data
    Return Invalid data 
    """
    processed_lines = []
    invalid_lines = []

    with open(file_path, 'r', encoding='utf-8') as infile:
        for line_num, line in enumerate(infile, start=1):
            # Remove leading/trailing whitespace and unwanted characters
            original_line = line.strip()
            line = re.sub(r'^[<>\s]+|[<>\s]+$', '', original_line)

            # Validate the line format
            reasons = validate_line(line)
            if reasons:
                invalid_lines.append({
                    "line_number": line_num,
                    "line_content": original_line,
                    "reason": "; ".join(reasons)
                })
            else:
                processed_lines.append(line)

    return '\n'.join(processed_lines), invalid_lines


@app.route('/download/<filename>')
def download_file(filename):
    """
    Serve a processed file for download.
    """
    file_path = os.path.join(PROCESSED_FOLDER, filename)
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")  # Debug log
        return jsonify({"error": "File not found."}), 404

    return send_from_directory(PROCESSED_FOLDER, filename, as_attachment=True)



if __name__ == '__main__':
    app.run(port=5012)
