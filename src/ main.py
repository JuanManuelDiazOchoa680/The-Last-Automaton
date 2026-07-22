import pygame
import os
from menu import draw_menu
from partida import draw_partida, generar_colisiones_contorno, draw_colisiones_debug
from protagonista import Robot

# Inicializar Pygame
pygame.init()

# ==========================================================
# VENTANA: se ajusta a la resolución real de tu PC dejando
# espacio para la barra de título y la barra de tareas, así
# los botones de cerrar/minimizar siempre quedan visibles.
# ==========================================================
ANCHO_DESEADO, ALTO_DESEADO = 1346, 768
MARGEN_VERTICAL = 90  # espacio reservado para barra de título + barra de tareas

info = pygame.display.Info()
ANCHO = min(ANCHO_DESEADO, info.current_w - 20)
ALTO = min(ALTO_DESEADO, info.current_h - MARGEN_VERTICAL)

pos_x = max(0, (info.current_w - ANCHO) // 2)
pos_y = 30
os.environ["SDL_VIDEO_WINDOW_POS"] = f"{pos_x},{pos_y}"

pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("The Last Automaton")

# Superficie intermedia donde dibujamos TODO. Sobre esta superficie es
# donde aplicamos el zoom de cámara antes de mandarla a la ventana real.
escena = pygame.Surface((ANCHO, ALTO))

# Control de fps
reloj = pygame.time.Clock()

# Estados del juego
MENU, INTRO, JUGANDO = "menu", "intro", "jugando"
estado_juego = MENU

boton_visible = True
rect_boton = pygame.Rect(0, 0, 0, 0)

# Generamos una sola vez los cubitos de colisión del mapa
colisiones_mapa = generar_colisiones_contorno()

robot = None
mostrar_debug = True  # tecla H para mostrar/ocultar hitboxes y colisiones

# ==========================================================
# CAMBIA AQUÍ EL EFECTO DE ZOOM AL ATERRIZAR
# ==========================================================
ZOOM_EXTRA_ATERRIZAJE = 0.18      # 0.18 = la escena se agranda un 18% de golpe
VELOCIDAD_RECUPERACION_ZOOM = 9.0 # que tan rápido vuelve a la normalidad (mas alto = mas rapido)
zoom_actual = 1.0

# Bucle principal del juego
ejecutando = True
while ejecutando:
    dt = reloj.tick(60) / 1000.0
    dt = min(dt, 1 / 30)  # evita saltos grandes de físicas si hay lag puntual

    # 1. Procesar eventos PRIMERO (así el salto nunca se pierde entre frames)
    salto_iniciado = False
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False

        elif evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_h:
                mostrar_debug = not mostrar_debug
            if evento.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                salto_iniciado = True

        elif evento.type == pygame.MOUSEBUTTONDOWN:
            if evento.button == 1:
                if estado_juego == MENU and boton_visible and rect_boton.collidepoint(evento.pos):
                    boton_visible = False
                    estado_juego = INTRO
                    robot = Robot(x_inicial=ANCHO // 2)
                    print("¡PLAY presionado! El robot empieza a caer del cielo...")

    # 2. Actualizar lógica
    if estado_juego != MENU and robot is not None:
        robot.mostrar_hitbox = mostrar_debug
        robot.actualizar(dt, pygame.key.get_pressed(), colisiones_mapa, salto_iniciado)

        if estado_juego == INTRO and robot.estado == "jugando":
            estado_juego = JUGANDO

        if robot.acaba_de_aterrizar:
            zoom_actual = 1.0 + ZOOM_EXTRA_ATERRIZAJE

    # El zoom siempre se va relajando de vuelta a 1.0
    zoom_actual += (1.0 - zoom_actual) * min(1.0, VELOCIDAD_RECUPERACION_ZOOM * dt)

    # 3. Dibujar TODO sobre la escena (no directo a la ventana)
    escena.fill((50, 130, 235))
    draw_partida(escena)

    if estado_juego == MENU:
        if boton_visible:
            rect_boton = draw_menu(escena)
    else:
        if robot is not None:
            robot.dibujar(escena)

    if mostrar_debug:
        draw_colisiones_debug(escena)

    # 4. Aplicar el zoom de cámara (centrado en el robot) y mandarlo a la ventana
    if abs(zoom_actual - 1.0) < 0.001:
        pantalla.blit(escena, (0, 0))
    else:
        ancho_zoom = max(1, round(ANCHO * zoom_actual))
        alto_zoom = max(1, round(ALTO * zoom_actual))
        escena_escalada = pygame.transform.smoothscale(escena, (ancho_zoom, alto_zoom))

        if robot is not None:
            foco_x, foco_y = robot.rect.center
        else:
            foco_x, foco_y = ANCHO // 2, ALTO // 2

        fx = foco_x / ANCHO
        fy = foco_y / ALTO
        offset_x = round(fx * ANCHO - fx * ancho_zoom)
        offset_y = round(fy * ALTO - fy * alto_zoom)

        pantalla.blit(escena_escalada, (offset_x, offset_y))

    # 5. Actualizar la pantalla
    pygame.display.flip()

pygame.quit()