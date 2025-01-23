import requests
import base64
import pygame
import io
import tempfile
import os
import cv2  # Importar OpenCV

# Configuración de la API
API_URL = "https://pantalla-anuncios-rasp.onrender.com/media2"

# Definir color de fondo
BACKGROUND_COLOR = (50, 50, 50)  # Gris oscuro (puedes elegir otro color si lo prefieres)
TEXT_COLOR = (255, 255, 255)  # Blanco para el texto

def display_images_on_screen():
    pygame.init()
    info = pygame.display.Info()
    screen_width = info.current_w
    screen_height = info.current_h
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
    pygame.display.set_caption("Media Display")

    clock = pygame.time.Clock()
    last_media_content = None

    while True:
        try:
            # Solicitar a la API con long polling
            response = requests.get(API_URL, stream=True)  # Usar stream=True para mantener la conexión abierta
            media_content = response.json()

            # Verificar si ha cambiado el contenido de imagen
            if media_content != last_media_content:
                last_media_content = media_content

            # Rellenar el fondo con un color
            screen.fill(BACKGROUND_COLOR)

            # Mostrar imágenes 1 y 2 ajustadas y centradas en la parte inferior
            if media_content.get("image1") and "limpiar" not in media_content["image1"].lower():
                display_image(screen, media_content["image1"], 0, screen_height // 2, screen_width // 2, screen_height // 2, "Imagen 1")
            else:
                display_text(screen, "Imagen 1", 0, screen_height // 2, screen_width // 2, screen_height // 2)

            if media_content.get("image2") and "limpiar" not in media_content["image2"].lower():
                display_image(screen, media_content["image2"], screen_width // 2, screen_height // 2, screen_width // 2, screen_height // 2, "Imagen 2")
            else:
                display_text(screen, "Imagen 2", screen_width // 2, screen_height // 2, screen_width // 2, screen_height // 2)

            # Reproducir video en la parte superior
            if media_content.get("video") and "limpiar" not in media_content["video"].lower():
                play_video(screen, media_content["video"], 0, 0, screen_width, screen_height // 2)
            else:
                display_text(screen, "Video", 0, 0, screen_width, screen_height // 2)

            pygame.display.flip()

        except Exception as e:
            print(f"Error al obtener o mostrar contenido multimedia: {e}")

        clock.tick(30)  # Ajustar a 30 FPS para evitar sobrecarga

def display_image(screen, base64_string, x, y, width, height, label):
    try:
        image_data = base64.b64decode(base64_string)
        image = pygame.image.load(io.BytesIO(image_data))
        
        # Redimensionar la imagen para que encaje en el contenedor sin cambiar sus proporciones
        img_rect = image.get_rect()
        scale_ratio = min(width / img_rect.width, height / img_rect.height)
        new_width = int(img_rect.width * scale_ratio)
        new_height = int(img_rect.height * scale_ratio)
        image = pygame.transform.scale(image, (new_width, new_height))
        
        # Obtener el color promedio de la imagen para el fondo
        avg_color = pygame.transform.average_color(image)
        screen.fill(avg_color, (x, y, width, height))

        # Centrar la imagen en su respectiva área sin hacerla más grande que su contenedor
        img_rect = image.get_rect()
        img_rect.topleft = (x + (width - img_rect.width) // 2, y + (height - img_rect.height) // 2)
        screen.blit(image, img_rect)
    except Exception as e:
        print(f"Error al convertir imagen ({label}): {e}")
        display_text(screen, label, x, y, width, height)

def play_video(screen, base64_string, x, y, width, height):
    try:
        # Decodificar el Base64 a un archivo temporal
        video_data = base64.b64decode(base64_string)
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
        temp_file.write(video_data)
        temp_file.close()

        # Usar OpenCV para reproducir el video
        cap = cv2.VideoCapture(temp_file.name)
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # Obtener dimensiones del frame
            frame_height, frame_width = frame.shape[:2]
            
            # Calcular la relación de escala para mantener las proporciones
            scale_ratio = min(width / frame_width, height / frame_height)
            new_width = int(frame_width * scale_ratio)
            new_height = int(frame_height * scale_ratio)

            # Redimensionar el frame
            frame = cv2.resize(frame, (new_width, new_height))

            # Convertir frame de BGR a RGB para pygame
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Crear la superficie de pygame
            frame_surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
            
            # Centrar el frame redimensionado en el contenedor
            frame_rect = frame_surface.get_rect()
            frame_rect.topleft = (x + (width - new_width) // 2, y + (height - new_height) // 2)

            # Dibujar el fondo
            screen.fill(BACKGROUND_COLOR, (x, y, width, height))
            
            # Dibujar el frame en la pantalla
            screen.blit(frame_surface, frame_rect)
            pygame.display.update()
            pygame.time.delay(int(1000 / cap.get(cv2.CAP_PROP_FPS)))

        cap.release()
        # Eliminar el archivo temporal
        os.remove(temp_file.name)

    except Exception as e:
        print(f"Error al reproducir video: {e}")
        display_text(screen, "Video", x, y, width, height)

def display_text(screen, text, x, y, width, height):
    font = pygame.font.Font(None, 36)
    text_surface = font.render(text, True, TEXT_COLOR)
    text_rect = text_surface.get_rect(center=(x + width // 2, y + height // 2))

    # Dibujar el fondo y el texto centrado
    screen.fill(BACKGROUND_COLOR, (x, y, width, height))
    screen.blit(text_surface, text_rect)

if __name__ == '__main__':                              
    display_images_on_screen()
