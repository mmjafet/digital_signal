from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_socketio import SocketIO
import base64

app = Flask(_name_)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")  # Habilitamos WebSocket

media_content = {
    "video": None,  # Base64 del video
    "image1": None,  # Base64 de la imagen 1
    "image2": None,  # Base64 de la imagen 2
    "image3": None
}

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

    # Emitimos un evento indicando que hubo un cambio
    socketio.emit('media_updated', {"position": position, "message": "Contenido actualizado"})
    
    return jsonify({"message": f"Contenido actualizado en '{position}'"}), 200

@app.route('/media', methods=['GET'])
def get_media():
    return jsonify(media_content)

@app.route('/')
def display_web():
    return render_template("index.html")

@app.route('/da')
def display():
    return render_template("media.html", media=media_content)

if _name_ == '_main_':
    socketio.run(app, host='0.0.0.0', port=9999)