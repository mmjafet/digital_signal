import requests
import base64
import pygame
import cv2
import numpy as np
from PIL import Image
import io

# Configuración de la API
API_URL = "http://172.168.2.209:9999/media"  # Cambia 172.168.2.209 por la IP del servidor correcta


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

    while True:
        try:
            # Obtener el contenido multimedia desde la API
            response = requests.get(API_URL)
            media_content = response.json()

            # Si todo el contenido está vacío, limpiar pantalla con divisiones y mensaje
            if all(value is None for value in media_content.values()):
                clear_screen_with_message(screen, screen_width, screen_height)
                pygame.display.flip()
                clock.tick(1)  # Esperar un segundo antes de consultar nuevamente
                continue

            # Renderizar el contenido en la pantalla
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
            print(f"Error al obtener o mostrar contenido multimedia: {e}")

        clock.tick(1)  # Actualiza una vez por segundo

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

        cap.release()  # Liberar el video

    except Exception as e:
        print(f"Error al reproducir video: {e}")

def base64_to_surface(base64_string, max_width, max_height):
    try:
        image_data = base64.b64decode(base64_string)
        image = Image.open(io.BytesIO(image_data))

        image.thumbnail((max_width, max_height), Image.ANTIALIAS)

        # Convertir la imagen redimensionada a una superficie de Pygame
        mode = image.mode
        size = image.size
        data = image.tobytes()
        return pygame.image.fromstring(data, size, mode)
    except Exception as e:
        print(f"Error al convertir imagen: {e}")
        return None

def clear_screen_with_message(screen, screen_width, screen_height):
    # Fondo de color gris claro
    screen.fill((200, 200, 200))

    pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(0, 0, screen_width, screen_height // 2), 3)  # División superior
    pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(0, screen_height // 2, screen_width // 2, screen_height // 2), 3)  # División izquierda
    pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(screen_width // 2, screen_height // 2, screen_width // 2, screen_height // 2), 3)  # División derecha

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