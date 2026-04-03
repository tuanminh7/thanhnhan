import os
import uuid
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Nạp biến môi trường từ file .env (nếu có)
load_dotenv()

from engine.ai_core import analyze_content
from engine.db_manager import save_scan, get_all_history, get_scan_by_id

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max
app.secret_key = 'supersecretkey'

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    text_content = request.form.get('text_content', '')
    image_file = request.files.get('image_file')
    
    image_path = None
    if image_file and allowed_file(image_file.filename):
        filename = secure_filename(f"{uuid.uuid4()}_{image_file.filename}")
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image_file.save(image_path)

    # Call AI Engine
    try:
        result = analyze_content(text_content, image_path)
        if not result.get("error"):
            save_scan(text_content, image_path, result)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/history')
def history():
    data = get_all_history()
    return jsonify(data)

@app.route('/history/<int:scan_id>')
def history_detail(scan_id):
    data = get_scan_by_id(scan_id)
    if data:
        return jsonify(data)
    return jsonify({"error": "Không tìm thấy"}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)
