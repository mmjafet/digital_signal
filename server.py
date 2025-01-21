from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_socketio import SocketIO
import signal
import base64

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

media_content = {
    "video": None,
    "image1": None,
    "image2": None,
    "image3": None
}

@app.route('/upload', methods=['POST'])
def upload_media():
    global media_content
    try:
        data = request.json
        if 'video' in data:
            media_content['video'] = data['video']
        if 'image1' in data:
            media_content['image1'] = data['image1']
        if 'image2' in data:
            media_content['image2'] = data['image2']
        if 'image3' in data:
            media_content['image3'] = data['image3']
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/media', methods=['GET'])
def get_media():
    return jsonify(media_content), 200

def signal_handler(sig, frame):
    print('Shutting down server...')
    socketio.stop()

signal.signal(signal.SIGINT, signal_handler)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)