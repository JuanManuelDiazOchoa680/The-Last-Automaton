import pygame
import os
from menu import draw_menu
from partida import draw_partida

# Inicializar Pygame
pygame.init()

# Configurar dimensiones de la ventana
ANCHO, ALTO = 1366, 768
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("The Last Automaton")

# Control de fps
reloj = pygame.time.Clock()

# Estado del juego
boton_visible = True
rect_boton = pygame.Rect(0, 0, 0, 0) # Rectángulo vacío inicial

# Bucle principal del juego
ejecutando = True
while ejecutando:
    # ==========================================
    # 1. LIMPIAR LA PANTALLA ANTES DE DIBUJAR
    # ==========================================
    # Pintamos toda la ventana de azul claro para borrar el fotograma anterior
    pantalla.fill((50, 130, 235)) 
    
    # 2. Dibujar el fondo del desierto
    draw_partida(pantalla)
    
    # 3. Dibujar el botón PLAY solo si es visible
    if boton_visible:
        rect_boton = draw_menu(pantalla)
    
    # 4. Detectar eventos
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False
            
        elif evento.type == pygame.MOUSEBUTTONDOWN:
            if evento.button == 1: # Clic izquierdo
                # Si hacemos clic dentro del botón play
                if boton_visible and rect_boton.collidepoint(evento.pos):
                    boton_visible = False # Cambiamos el estado a invisible
                    print("¡PLAY presionado! El botón desaparece.")

    # 5. Actualizar la pantalla
    pygame.display.flip()
    reloj.tick(60) # Forzar 60 FPS

pygame.quit()