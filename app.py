import requests
from flask import Flask, render_template, Response
import time
import threading
import base64

# Configuración de la API
API_URL = "https://pantalla-anuncios-rasp.onrender.com/media"

app = Flask(__name__)

# Función para obtener el video desde la API y enviarlo al cliente
def generate_video():
    while True:
        try:
            # Hacer la solicitud a la API para obtener el video
            response = requests.get(API_URL)
            media_content = response.json()

            if media_content["video"]:
                # Obtener el video en base64
                video_base64 = media_content["video"]
                video_data = base64.b64decode(video_base64)

                # Enviar el video en fragmentos al cliente
                yield (b'--frame\r\n'
                       b'Content-Type: video/mp4\r\n\r\n' + video_data + b'\r\n')
            time.sleep(2)  # Pausar un poco antes de la siguiente solicitud
        except Exception as e:
            print(f"Error al obtener el video desde la API: {e}")
            time.sleep(5)  # Pausar antes de intentar nuevamente

# Ruta para la página principal
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para transmitir el video en tiempo real
@app.route('/video')
def video():
    return Response(generate_video(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
