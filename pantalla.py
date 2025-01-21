import requests
import base64                                                                                                                                                                                                                                                                                                                                                               
import pygame
import io

# Configuración de la API
API_URL = "https://pantalla-anuncios-rasp.onrender.com/media"

# Definir color de fondo
BACKGROUND_COLOR = (50, 50, 50)  # Gris oscuro (puedes elegir otro color si lo prefieres)

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
            if media_content.get("image1"):
                display_image(screen, media_content["image1"], 0, screen_height // 2, screen_width // 2, screen_height // 2, adjust_size=False)

            if media_content.get("image2"):
                display_image(screen, media_content["image2"], screen_width // 2, screen_height // 2, screen_width // 2, screen_height // 2, adjust_size=False)

            # Mostrar imagen 3 en la parte superior sin ajustar su tamaño
            if media_content.get("image3"):
                display_image(screen, media_content["image3"], 0, 0, screen_width, screen_height // 2, adjust_size=False)

            pygame.display.flip()

        except Exception as e:
            print(f"Error al obtener o mostrar contenido multimedia: {e}")

        clock.tick(30)  # Ajustar a 30 FPS para evitar sobrecarga

def display_image(screen, base64_string, x, y, width, height, adjust_size=True):
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
        print(f"Error al convertir imagen: {e}")

if __name__ == '__main__':
    display_images_on_screen()
