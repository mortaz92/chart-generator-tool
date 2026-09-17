import os
from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS

# Serviamo i file statici direttamente dalla radice dopo il build
app = Flask(__name__, static_folder='static', static_url_path='')
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
    if os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(debug=True, port=4000)
