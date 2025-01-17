import requests
import base64
import pygame
import cv2
import os
import time

# Configuración de la API
API_URL = "https://pantalla-anuncios-rasp.onrender.com/media"
VIDEO_DIR = "videos"
VIDEO_FILENAME = os.path.join(VIDEO_DIR, "video.mp4")
os.makedirs(VIDEO_DIR, exist_ok=True)

# Para almacenar la última marca de tiempo del video
last_video_timestamp = None

# Función para mostrar en pantalla
def display_on_screen():
    global last_video_timestamp
    pygame.init()
    info = pygame.display.Info()
    screen_width = info.current_w
    screen_height = info.current_h
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
    pygame.display.set_caption("Media Display")

    clock = pygame.time.Clock()
    cap = None

    while True:
        try:
            # Revisamos si hay un nuevo video cada 10 segundos
            check_new_video()

            # Si no hay video cargado o ha cambiado, lo cargamos
            if not cap or not cap.isOpened():
                cap = cv2.VideoCapture(VIDEO_FILENAME)

            if cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frame_height, frame_width = frame.shape[:2]
                    scale_factor = min(screen_width / frame_width, screen_height / frame_height)
                    new_width = int(frame_width * scale_factor)
                    new_height = int(frame_height * scale_factor)
                    frame = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_AREA)

                    frame_surface = pygame.surfarray.make_surface(frame)
                    frame_surface = pygame.transform.scale(frame_surface, (new_width, new_height))

                    # Calcular las coordenadas para centrar el video
                    x_offset = (screen_width - new_width) // 2
                    y_offset = (screen_height - new_height) // 2
                    screen.blit(frame_surface, (x_offset, y_offset))

                    pygame.display.flip()
                else:
                    cap.release()

            clock.tick(30)  # Limitar la tasa de fotogramas a 30 FPS

        except Exception as e:
            print(f"Error al obtener o mostrar contenido multimedia: {e}")

# Función para comprobar si hay un nuevo video
def check_new_video():
    global last_video_timestamp
    try:
        response = requests.get(API_URL)
        media_content = response.json()

        if media_content.get("video"):
            new_video_timestamp = media_content.get("timestamp")
            if new_video_timestamp != last_video_timestamp:
                print("Nuevo video encontrado. Cargando...")
                video_base64 = media_content["video"]
                save_video_from_base64(video_base64)
                last_video_timestamp = new_video_timestamp

    except Exception as e:
        print(f"Error al comprobar el video: {e}")

# Función para guardar el video desde Base64
def save_video_from_base64(base64_string):
    try:
        video_data = base64.b64decode(base64_string)
        with open(VIDEO_FILENAME, "wb") as video_file:
            video_file.write(video_data)
        print(f"Video guardado exitosamente en {VIDEO_FILENAME}")
    except Exception as e:
        print(f"Error al guardar el video: {e}")

if __name__ == '__main__':
    display_on_screen()