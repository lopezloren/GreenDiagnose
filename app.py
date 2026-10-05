"""
GreenDiagnose - Flask Application Skeleton
Final design: species-specific classification, accountless, no runtime admin.

Folder structure this file assumes:
  app.py                 <- this file
  requirements.txt
  /models/                <- trained .h5/.tflite files, one per species (or one shared model)
  /uploads/                <- retained diagnosis photos
  /static/                 <- frontend assets (if serving templates directly)
  /templates/               <- Jinja2 templates (if not using a separate frontend)

Run with: flask run  (after setting FLASK_APP=app.py)
"""

from flask import Flask, request, jsonify, render_template, send_from_directory
import os

from db import fetch_all, execute
from cnn_classifier import classify_image
from rule_engine import get_questions_for_species, compute_diagnosis

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max upload

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- FRONTEND & PWA ROUTES ---
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload')
def upload_page():
    # Now correctly queries 'plant_species' to match schema.sql
    species_list = fetch_all("SELECT id, common_name, scientific_name FROM plant_species")
    return render_template('upload.html', species=species_list)

@app.route('/manifest.json')
def serve_manifest():
    return send_from_directory('static', 'manifest.json')

@app.route('/sw.js')
def serve_sw():
    return send_from_directory('static', 'sw.js')

# --- BACKEND API ROUTES ---
@app.route('/api/species', methods=['GET'])
def get_species():
    # Now correctly queries 'plant_species' to match schema.sql
    species_list = fetch_all("SELECT id, common_name, scientific_name FROM plant_species")
    return jsonify({"species": species_list})

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'file' not in request.files:
        return "No file uploaded", 400
        
    file = request.files['file']
    species_id =int (request.form.get('species_id'))
    
    if file.filename == '':
        return "No file selected", 400

    if not allowed_file(file.filename):
        return "Invalid file type. Please upload a valid image (PNG, JPG, JPEG).", 400 

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)

    predicted_disease_id, confidence = classify_image(filepath, species_id)
    model_path = os.path.join('models', f'{species_id}.h5')
    if not os.path.exists(model_path):
     return render_template('error.html', message="AI model for this species is still under training. Please check back soon!"), 400
    consent = 1 if request.form.get('consent_for_training') == '1' else 0
    # Pass 'consent' into your database session insertion query
    # --- NEW: Fetch dynamic questions from the database ---
    questions = get_questions_for_species(species_id)

    return render_template(
        'questionnaire.html', 
        species_id=species_id, 
        filename=file.filename,
        cnn_disease_id=predicted_disease_id,
        cnn_confidence=confidence,
        questions=questions  # Pass the questions to the HTML
    )

@app.route('/result', methods=['POST'])
def result():
    species_id = request.form.get('species_id')
    print(f"DEBUG: The species_id received is: {species_id}")
    # --- NEW: Dynamically grab all symptom answers from the form ---
    answers = []
    for key, value in request.form.items():
        if key.startswith('symptom_'):
            # Extract the ID number from the name (e.g., "symptom_5" -> 5)
            symptom_id = int(key.split('_')[1])
            answers.append({"symptom_id": symptom_id, "answer_value": value})
            
    # Pull the actual AI predictions passed from the questionnaire form
    cnn_disease_id = int(request.form.get('cnn_disease_id', 1))
    cnn_confidence = float(request.form.get('cnn_confidence', 0.8850))

    try:
        diagnoses = compute_diagnosis(species_id, cnn_disease_id, cnn_confidence, answers)
        
        if not diagnoses:
            return "Database is empty! We need to add diseases to MySQL first."
            
        top_result = diagnoses[0]
        
        display_confidence = f"{top_result['confidence'] * 100:.1f}%"
        if top_result.get('is_low_confidence'):
            display_confidence += " (Low Confidence - Consult Expert)"
            
        treatments = [top_result['treatment']]
        
        return render_template(
            'result.html',
            diagnosis=top_result['disease_name'],
            confidence=display_confidence,
            treatments=treatments
        )
    except Exception as e:
        return f"Database Error: {e}"
    
# --- SERVER STARTUP ---
if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    # host='0.0.0.0' tells Flask to listen on all network interfaces
    app.run(host='0.0.0.0', debug=True)
