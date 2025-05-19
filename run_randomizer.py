from flask import Flask, render_template, send_from_directory, request, jsonify
import os
import subprocess
import threading
import tempfile
import time
import uuid

app = Flask(__name__)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('.', path)

@app.route('/api/run-randomizer', methods=['POST'])
def run_randomizer():
    # Create a unique working directory
    work_dir = tempfile.mkdtemp()
    
    # Get uploaded ROM file
    if 'romFile' not in request.files:
        return jsonify({'error': 'No ROM file provided'}), 400
    
    rom_file = request.files['romFile']
    rom_path = os.path.join(work_dir, rom_file.filename)
    rom_file.save(rom_path)
    
    # Get settings from request
    settings = request.form.get('settings', '')
    
    # Run the randomizer JAR
    output_path = os.path.join(work_dir, f"randomized_{str(uuid.uuid4())}.gba")
    
    # Execute JAR with Java
    cmd = ['java', '-jar', 'randomizer.jar', '-i', rom_path, '-o', output_path, '-s', settings]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if result.returncode != 0:
            return jsonify({
                'error': 'Randomizer failed',
                'stdout': result.stdout,
                'stderr': result.stderr
            }), 500
        
        # Return the randomized ROM file
        return send_from_directory(os.path.dirname(output_path), os.path.basename(output_path), 
                                   as_attachment=True, 
                                   download_name=f"randomized_{os.path.basename(rom_file.filename)}")
    
    except subprocess.TimeoutExpired:
        return jsonify({'error': 'Randomizer timed out'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
