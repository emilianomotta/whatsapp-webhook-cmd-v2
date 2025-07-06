
from flask import Flask, jsonify
import json

app = Flask(__name__)

@app.route('/messages', methods=['GET'])
def get_messages():
    try:
        with open('messages.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Mantener procesamiento si existe
if __name__ == '__main__':
    app.run(debug=False)
