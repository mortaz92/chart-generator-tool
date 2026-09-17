import os
from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS

# Puntiamo direttamente alla cartella di build di Vite
dist_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'frontend', 'dist')
app = Flask(__name__, static_folder=dist_dir, static_url_path='')
CORS(app)

signals = []

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/signals', methods=['POST'])
def add_signal():
    data = request.json
    signals.append(data)
    return jsonify({"status": "success"}), 201

@app.route('/api/signals', methods=['GET'])
def get_signals():
    return jsonify(signals)

@app.route('/<path:path>')
def serve_static(path):
    if os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 4000))
    app.run(host='0.0.0.0', port=port)
