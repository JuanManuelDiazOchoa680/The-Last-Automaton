import pygame
import os

# Buscamos la ruta del desierto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUTA_DESIERTO = os.path.join(BASE_DIR, "assets", "images", "desierto.png")

# ==========================================================
# CAMBIA AQUÍ LA POSICIÓN Y EL TAMAÑO DEL DESIERTO
# ==========================================================
X_FONDO = 0       # Posición horizontal
Y_FONDO = 0       # Posición vertical
ANCHO_F = 1366    # Ancho del fondo
ALTO_F = 768      # Alto del fondo

_desierto_img = None
_colisiones_cache = None


def cargar_desierto():
    """Carga (una sola vez) la imagen original del desierto."""
    global _desierto_img
    if _desierto_img is None:
        try:
            _desierto_img = pygame.image.load(RUTA_DESIERTO).convert_alpha()
        except Exception as e:
            print(f"[Partida] No se pudo cargar el desierto: {e}")
            _desierto_img = pygame.Surface((ANCHO_F, ALTO_F), pygame.SRCALPHA)
    return _desierto_img


def generar_colisiones_contorno(umbral_alpha=20):
    """
    Genera un cubito de colisión (pygame.Rect) por cada píxel opaco de
    desierto.png que forme parte del CONTORNO del dibujo, es decir, que
    tenga al menos un vecino transparente (o esté en el borde de la imagen).

    Los píxeles interiores (rodeados de otros píxeles opacos) NO generan
    colisión porque nunca son alcanzables desde afuera del dibujo, así nos
    ahorramos código y mejoramos el rendimiento tal como pediste.

    El resultado se guarda en caché porque la imagen no cambia en tiempo real.
    """
    global _colisiones_cache
    if _colisiones_cache is not None:
        return _colisiones_cache

    img = cargar_desierto()
    ancho_img, alto_img = img.get_size()

    escala_x = ANCHO_F / ancho_img
    escala_y = ALTO_F / alto_img

    mask = pygame.mask.from_surface(img, umbral_alpha)

    cubitos = []
    ancho_rect = max(1, round(escala_x)) + 1
    alto_rect = max(1, round(escala_y)) + 1

    for y in range(alto_img):
        for x in range(ancho_img):
            if not mask.get_at((x, y)):
                continue

            es_contorno = False
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if nx < 0 or ny < 0 or nx >= ancho_img or ny >= alto_img:
                    es_contorno = True
                    break
                if not mask.get_at((nx, ny)):
                    es_contorno = True
                    break

            if es_contorno:
                rect_x = X_FONDO + x * escala_x
                rect_y = Y_FONDO + y * escala_y
                cubitos.append(pygame.Rect(round(rect_x), round(rect_y), ancho_rect, alto_rect))

    _colisiones_cache = cubitos
    print(f"[Partida] Generados {len(cubitos)} cubitos de colisión del contorno del desierto.")
    return cubitos


def draw_partida(pantalla):
    img = cargar_desierto()
    desierto_escalado = pygame.transform.scale(img, (ANCHO_F, ALTO_F))
    pantalla.blit(desierto_escalado, (X_FONDO, Y_FONDO))


def draw_colisiones_debug(pantalla):
    """Dibuja en verde todos los cubitos de colisión, para depurar visualmente."""
    for rect in generar_colisiones_contorno():
        pygame.draw.rect(pantalla, (0, 255, 0), rect, 1)