import pygame
import os

# Buscamos la ruta del robot (misma convención que menu.py / partida.py)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUTA_ROBOT = os.path.join(BASE_DIR, "assets", "images", "Robot_quieto.png")

# ==========================================================
# CAMBIA AQUÍ EL TAMAÑO DEL ROBOT EN PANTALLA
# ==========================================================
ANCHO_R = 35    # Ancho al que se escala el robot
ALTO_R = 35     # Alto al que se escala el robot

# ==========================================================
# CAMBIA AQUÍ LOS VALORES DE FÍSICA
# ==========================================================
GRAVEDAD = 1600              # px/s^2, qué tan rápido acelera al caer
VELOCIDAD_MOV = 240          # px/s, velocidad al moverse izquierda/derecha
VELOCIDAD_SALTO_MAX = 560    # px/s, impulso si mantienes presionado el salto
VELOCIDAD_SALTO_MIN = 190    # px/s, impulso si solo lo tocas rapidito (bien mínimo)
AMORTIGUACION_REBOTE = 0.4   # cuánto conserva de velocidad al rebotar (0-1)
UMBRAL_REBOTE = 60           # px/s, por debajo de esto el rebote se detiene
UMBRAL_IMPACTO_ZOOM = 150    # px/s, aterrizajes más fuertes que esto disparan el zoom de cámara


class Robot:
    def __init__(self, x_inicial, y_inicial=None):
        try:
            img_original = pygame.image.load(RUTA_ROBOT).convert_alpha()
        except Exception as e:
            print(f"[Protagonista] No se pudo cargar el robot, usando uno temporal: {e}")
            img_original = pygame.Surface((ANCHO_R, ALTO_R), pygame.SRCALPHA)
            img_original.fill((200, 60, 60, 255))

        # El sprite original mira hacia la IZQUIERDA. Precalculamos también
        # la versión espejada para cuando el robot se mueva a la derecha.
        # (si tu sprite en realidad mira a la derecha, solo invierte estas dos líneas)
        self.imagen_izquierda = pygame.transform.scale(img_original, (ANCHO_R, ALTO_R))
        self.imagen_derecha = pygame.transform.flip(self.imagen_izquierda, True, False)
        self.imagen = self.imagen_izquierda

        y_spawn = y_inicial if y_inicial is not None else -ALTO_R
        self.rect = pygame.Rect(int(x_inicial - ANCHO_R // 2), y_spawn, ANCHO_R, ALTO_R)

        self.vel_x = 0.0
        self.vel_y = 0.0
        self.en_suelo = False
        self.mirando_derecha = False

        # Estados: "cayendo_intro" (caída inicial con rebote) -> "jugando" (control del usuario)
        self.estado = "cayendo_intro"

        # Control de salto variable (tap = salto mínimo, mantener = salto máximo)
        self._saltando = False

        # Se pone en True durante UN solo frame cuando el robot acaba de
        # tocar el suelo con fuerza. main.py lo usa para disparar el zoom de cámara.
        self.acaba_de_aterrizar = False

        self.mostrar_hitbox = True

    # ------------------------------------------------------------------
    # Movimiento con resolución de colisiones eje por eje (estilo AABB)
    # ------------------------------------------------------------------
    def _mover_x(self, dx, colisiones):
        self.rect.x += round(dx)
        for c in colisiones:
            if self.rect.colliderect(c):
                if dx > 0:
                    self.rect.right = c.left
                elif dx < 0:
                    self.rect.left = c.right

    def _mover_y(self, dy, colisiones):
        self.rect.y += round(dy)
        self.en_suelo = False
        colisiono_abajo = False
        colisiono_arriba = False
        for c in colisiones:
            if self.rect.colliderect(c):
                if dy > 0:
                    self.rect.bottom = c.top
                    self.en_suelo = True
                    colisiono_abajo = True
                elif dy < 0:
                    self.rect.top = c.bottom
                    colisiono_arriba = True
        return colisiono_abajo, colisiono_arriba

    # ------------------------------------------------------------------
    # Lógica por estado
    # ------------------------------------------------------------------
    def _actualizar_intro(self, dt, colisiones):
        self.vel_y += GRAVEDAD * dt
        impacto_vy = self.vel_y

        abajo, arriba = self._mover_y(self.vel_y * dt, colisiones)

        if arriba:
            self.vel_y = 0

        if abajo:
            if abs(impacto_vy) < UMBRAL_REBOTE:
                # Ya casi no rebota -> terminó la intro, pasa a modo jugable
                self.vel_y = 0
                self.estado = "jugando"
                print("[Protagonista] Rebote terminado, ¡ya puedes moverte!")
            else:
                # Rebota hacia arriba conservando una fracción de la velocidad de impacto
                self.vel_y = -impacto_vy * AMORTIGUACION_REBOTE

    def _actualizar_juego(self, dt, teclas, colisiones, salto_iniciado):
        self.vel_x = 0
        if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
            self.vel_x = -VELOCIDAD_MOV
            self.mirando_derecha = False
        if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
            self.vel_x = VELOCIDAD_MOV
            self.mirando_derecha = True

        # --- Salto variable: tocar rapidito = salto mínimo, mantener = salto máximo ---
        # salto_iniciado viene de un evento KEYDOWN real (main.py), no de comparar
        # el teclado frame a frame, así no se pierde ningún toque por rápido que sea.
        salto_mantenido = teclas[pygame.K_SPACE] or teclas[pygame.K_UP] or teclas[pygame.K_w]

        if salto_iniciado and self.en_suelo:
            self.vel_y = -VELOCIDAD_SALTO_MAX
            self._saltando = True

        if self._saltando:
            if not salto_mantenido:
                # Se soltó la tecla mientras subía -> cortamos el salto al mínimo
                if self.vel_y < -VELOCIDAD_SALTO_MIN:
                    self.vel_y = -VELOCIDAD_SALTO_MIN
                self._saltando = False
            elif self.vel_y >= 0:
                # Ya empezó a caer -> el salto terminó de todos modos
                self._saltando = False

        self.vel_y += GRAVEDAD * dt

        self._mover_x(self.vel_x * dt, colisiones)
        abajo, arriba = self._mover_y(self.vel_y * dt, colisiones)
        if abajo or arriba:
            self.vel_y = 0
            if abajo:
                self._saltando = False

    def actualizar(self, dt, teclas, colisiones, salto_iniciado=False):
        self.acaba_de_aterrizar = False
        estaba_en_suelo = self.en_suelo
        vel_y_antes_del_frame = self.vel_y

        if self.estado == "cayendo_intro":
            self._actualizar_intro(dt, colisiones)
        elif self.estado == "jugando":
            self._actualizar_juego(dt, teclas, colisiones, salto_iniciado)

        # Si justo este frame pasó de estar en el aire a tocar el suelo, y venía
        # con suficiente velocidad, avisamos para que main.py dispare el zoom.
        if self.en_suelo and not estaba_en_suelo and abs(vel_y_antes_del_frame) > UMBRAL_IMPACTO_ZOOM:
            self.acaba_de_aterrizar = True

    def dibujar(self, pantalla):
        imagen_actual = self.imagen_derecha if self.mirando_derecha else self.imagen_izquierda
        pantalla.blit(imagen_actual, self.rect)
        if self.mostrar_hitbox:
            pygame.draw.rect(pantalla, (255, 0, 0), self.rect, 2)