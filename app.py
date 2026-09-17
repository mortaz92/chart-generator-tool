import os
from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS

# Percorso assoluto per evitare errori di path su Render
base_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(base_dir, 'static')

app = Flask(__name__, static_folder=static_dir, static_url_path='')
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

# Catch-all per il routing di React (SPA)
@app.route('/<path:path>')
def serve_static(path):
    # Se il file esiste nella cartella static, servilo
    if os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    # Altrimenti, torna all'index di React
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 4000))
    app.run(host='0.0.0.0', port=port)
