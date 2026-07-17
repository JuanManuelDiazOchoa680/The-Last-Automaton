import pygame
import os

# Buscamos la ruta del desierto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUTA_DESIERTO = os.path.join(BASE_DIR, "assets", "images", "desierto.png")

def draw_partida(pantalla):
    try:
        # Cargamos la imagen del desierto
        desierto_img = pygame.image.load(RUTA_DESIERTO).convert_alpha()
    except Exception as e:
        # Fondo naranja desierto de respaldo si no hay imagen
        pantalla.fill((217, 160, 91)) 
        return

    # ==========================================================
    # CAMBIA AQUÍ LA POSICIÓN Y EL TAMAÑO DEL DESIERTO
    # ==========================================================
    X_FONDO = 0       # Posición horizontal
    Y_FONDO = 0       # Posición vertical
    ANCHO_F = 1366    # Ancho del fondo
    ALTO_F = 768      # Alto del fondo

    # Escalamos la imagen del fondo
    desierto_escalado = pygame.transform.scale(desierto_img, (ANCHO_F, ALTO_F))
    
    # Dibujamos el desierto de fondo
    pantalla.blit(desierto_escalado, (X_FONDO, Y_FONDO))