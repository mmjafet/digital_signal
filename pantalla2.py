import requests
import base64
import pygame
import cv2
import numpy as np
from PIL import Image
import io
from websocket import create_connection
import threading

# Configuración de la API y WebSocket
API_URL = "http://172.168.0.104:9999/media"  # Cambia la IP del servidor correcta
WS_URL = "ws://172.168.0.104:9999/socket.io/?transport=websocket"  # URL del WebSocket

# Pygame - Mostrar en la pantalla de la Raspberry Pi
def display_on_screen():
    pygame.init()
    # Configuración de la pantalla
    info = pygame.display.Info()
    screen_width = info.current_w
    screen_height = info.current_h
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
    pygame.display.set_caption("Media Display")

    clock = pygame.time.Clock()

    # Hilo para manejar la recepción de mensajes del WebSocket
    def websocket_listener():
        ws = create_connection(WS_URL)
        while True:
            try:
                result = ws.recv()
                if result:
                    handle_websocket_message(result, screen, screen_width, screen_height)
            except Exception as e:
                print(f"Error al recibir mensaje del WebSocket: {e}")
                break

    # Iniciar el hilo del WebSocket
    threading.Thread(target=websocket_listener, daemon=True).start()

    # Mantener la ventana abierta
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        clock.tick(60)

def handle_websocket_message(message, screen, screen_width, screen_height):
    try:
        response = requests.get(API_URL)
        media_content = response.json()

        screen.fill((0, 0, 0))  # Fondo negro

        # Mostrar video
        if media_content["video"]:
            play_video_from_base64(media_content["video"], screen_width, screen_height)

        # Mostrar imagen 1
        if media_content["image1"]:
            img_surface = base64_to_surface(media_content["image1"], screen_width // 2, screen_height // 2)
            if img_surface:
                screen.blit(img_surface, (0, screen_height // 2))

        # Mostrar imagen 2 o GIF
        if media_content["image2"]:
            img_surface = base64_to_surface(media_content["image2"], screen_width // 2, screen_height // 2)
            if img_surface:
                screen.blit(img_surface, (screen_width // 2, screen_height // 2))

        pygame.display.flip()

    except Exception as e:
        print(f"Error al actualizar contenido multimedia: {e}")

def play_video_from_base64(base64_string, screen_width, screen_height):
    try:
        # Decodificar el video Base64
        video_data = base64.b64decode(base64_string)
        video_file = io.BytesIO(video_data)

        with open("temp_video.mp4", "wb") as f:
            f.write(video_file.read())

        cap = cv2.VideoCapture("temp_video.mp4")

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.resize(frame, (screen_width, screen_height))
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_surface = pygame.surfarray.make_surface(frame_rgb)

            screen.blit(frame_surface, (0, 0))
            pygame.display.flip()
            pygame.time.delay(30)

        cap.release()

    except Exception as e:
        print(f"Error al reproducir video: {e}")

def base64_to_surface(base64_string, max_width, max_height):
    try:
        image_data = base64.b64decode(base64_string)
        image = Image.open(io.BytesIO(image_data))

        image.thumbnail((max_width, max_height), Image.LANCZOS)

        mode = image.mode
        size = image.size
        data = image.tobytes()
        return pygame.image.fromstring(data, size, mode)
    except Exception as e:
        print(f"Error al convertir imagen: {e}")
        return None

def clear_screen_with_message(screen, screen_width, screen_height):
    screen.fill((200, 200, 200))

    pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(0, 0, screen_width, screen_height // 2), 3)
    pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(0, screen_height // 2, screen_width // 2, screen_height // 2), 3)
    pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(screen_width // 2, screen_height // 2, screen_width // 2, screen_height // 2), 3)

    draw_text(screen, "VIDEO", screen_width // 2, screen_height // 4, (0, 0, 0), screen_width)
    draw_text(screen, "IMAGEN 1", screen_width // 4, screen_height * 3 // 4, (0, 0, 0), screen_width)
    draw_text(screen, "IMAGEN 2", screen_width * 3 // 4, screen_height * 3 // 4, (0, 0, 0), screen_width)

def draw_text(surface, text, x, y, color, screen_width, font_size=24):
    pygame.font.init()
    font = pygame.font.SysFont("Arial", font_size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    surface.blit(text_surface, text_rect)

if __name__ == '__main__':
    display_on_screen()
