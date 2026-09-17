import os
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Abilita CORS per il frontend

# Simulazione database segnali (in futuro usiamo PostgreSQL/Drizzle)
signals = []

@app.route('/api/signals', methods=['POST'])
def add_signal():
    data = request.json
    signals.append(data)
    return jsonify({"status": "success", "message": "Signal received"}), 201

@app.route('/api/signals', methods=['GET'])
def get_signals():
    return jsonify(signals)

if __name__ == '__main__':
    app.run(debug=True, port=4000)
