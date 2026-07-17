import pygame
import os

# Buscamos la ruta de la imagen
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUTA_BOTON = os.path.join(BASE_DIR, "assets", "images", "boton_play.png")

def draw_menu(pantalla):
    try:
        # Cargamos la imagen respetando su transparencia original (.png)
        boton_play_img = pygame.image.load(RUTA_BOTON).convert_alpha()
    except Exception as e:
        print(f"[Menu] No se pudo cargar el botón, usando uno temporal: {e}")
        # Botón de respaldo si no encuentra la imagen
        boton_play_img = pygame.Surface((300, 100))
        boton_play_img.fill((100, 100, 100))

    # ==========================================================
    # CAMBIA AQUÍ LA POSICIÓN Y EL TAMAÑO INDEPENDIENTE DEL BOTÓN
    # ==========================================================
    X_BOTON = 600  # Posición horizontal (X)
    Y_BOTON = 400    # Posición vertical (Y)
    ANCHO_B = 200   # Ancho al que quieres escalar la imagen
    ALTO_B = 150     # Alto al que quieres escalar la imagen

    # Escalamos la imagen al tamaño que tú elijas
    boton_escalado = pygame.transform.scale(boton_play_img, (ANCHO_B, ALTO_B))
    
    # Lo dibujamos en las coordenadas exactas
    pantalla.blit(boton_escalado, (X_BOTON, Y_BOTON))
    
    # Devolvemos el rectángulo del botón para poder detectar el clic en main.py
    return pygame.Rect(X_BOTON, Y_BOTON, ANCHO_B, ALTO_B)