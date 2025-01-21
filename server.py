from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import base64

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app)

media_content = {
    "video": None,  # Base64 del video
    "image1": None,  # Base64 de la imagen 1
    "image2": None,  # Base64 de la imagen 2
    "image3": None
}

@app.route('/da')
def display():
    return render_template("media.html", media=media_content)

@app.route('/upload', methods=['POST'])
def upload():
    data = request.json
    if not data or 'position' not in data or 'file' not in data:
        return jsonify({"error": "Datos inválidos"}), 400

    position = data['position']
    file_data = data['file']

    if position not in media_content:
        return jsonify({"error": f"Posición '{position}' no válida"}), 400

    media_content[position] = file_data
    
    # Emitir un evento de WebSocket para notificar a los clientes
    socketio.emit('new_media', {"position": position, "file": file_data})
    return jsonify({"message": f"Contenido actualizado en '{position}'"}), 200

@app.route('/media', methods=['GET'])
def get_media():
    return jsonify(media_content)

@app.route('/')
def display_web():
    return render_template("index.html")

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=9999)
