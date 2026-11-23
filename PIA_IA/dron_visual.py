import math
import sys
import pygame

pygame.init()

# Configuración de ventana
WIDTH, HEIGHT = 1150, 650
PANEL_X = 760
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PIA PDDL - Simulación Dron de Entregas")
clock = pygame.time.Clock()

# Fuentes
FONT_TITLE = pygame.font.SysFont("dejavusans", 22, bold=True)
FONT_SUB = pygame.font.SysFont("dejavusans", 16, bold=True)
FONT_TEXT = pygame.font.SysFont("dejavusans", 14)
FONT_MONO = pygame.font.SysFont("dejavusansmono", 14)
FONT_MONO_BOLD = pygame.font.SysFont("dejavusansmono", 15, bold=True)

# Colores
BG = (18, 22, 30)
PANEL_BG = (26, 31, 43)
CARD_BG = (36, 43, 59)
BORDER = (62, 74, 98)
WHITE = (240, 244, 248)
MUTED = (148, 163, 184)
BLUE = (56, 189, 248)
GREEN = (52, 211, 153)
RED = (248, 113, 113)
AMBER = (251, 191, 36)
PURPLE = (167, 139, 250)

# Coordenadas de ubicaciones en el canvas izquierdo
LOCATIONS = {
    "base": (155, 400),
    "almacen": (380, 195),
    "cliente": (605, 400),
}

# Definición de los 7 pasos del plan + estado inicial
STEPS = [
    {
        "action": "Estado Inicial (:init)",
        "drone_pos": "base",
        "battery": True,
        "carrying": False,
        "pkg_pos": "almacen",
        "delivered": False,
        "pre": ["(en dron1 base)", "(bateria-alta dron1)", "(libre dron1)", "(paquete-en paq1 almacen)"],
        "eff": ["Inicio del escenario"],
    },
    {
        "action": "(volar dron1 base almacen)",
        "drone_pos": "almacen",
        "battery": False,
        "carrying": False,
        "pkg_pos": "almacen",
        "delivered": False,
        "pre": ["(en dron1 base)", "(bateria-alta dron1)"],
        "eff": ["+ (en dron1 almacen)", "- (en dron1 base)", "- (bateria-alta dron1)"],
    },
    {
        "action": "(recoger dron1 paq1 almacen)",
        "drone_pos": "almacen",
        "battery": False,
        "carrying": True,
        "pkg_pos": None,
        "delivered": False,
        "pre": ["(en dron1 almacen)", "(paquete-en paq1 almacen)", "(libre dron1)"],
        "eff": ["+ (llevando dron1 paq1)", "- (paquete-en paq1 almacen)", "- (libre dron1)"],
    },
    {
        "action": "(recargar dron1 almacen)",
        "drone_pos": "almacen",
        "battery": True,
        "carrying": True,
        "pkg_pos": None,
        "delivered": False,
        "pre": ["(en dron1 almacen)", "(estacion-carga almacen)"],
        "eff": ["+ (bateria-alta dron1)"],
    },
    {
        "action": "(volar dron1 almacen cliente)",
        "drone_pos": "cliente",
        "battery": False,
        "carrying": True,
        "pkg_pos": None,
        "delivered": False,
        "pre": ["(en dron1 almacen)", "(bateria-alta dron1)"],
        "eff": ["+ (en dron1 cliente)", "- (en dron1 almacen)", "- (bateria-alta dron1)"],
    },
    {
        "action": "(entregar dron1 paq1 cliente)",
        "drone_pos": "cliente",
        "battery": False,
        "carrying": False,
        "pkg_pos": "cliente",
        "delivered": True,
        "pre": ["(en dron1 cliente)", "(llevando dron1 paq1)", "(destino paq1 cliente)"],
        "eff": ["+ (entregado paq1)", "+ (libre dron1)", "- (llevando dron1 paq1)"],
    },
    {
        "action": "(recargar dron1 cliente)",
        "drone_pos": "cliente",
        "battery": True,
        "carrying": False,
        "pkg_pos": "cliente",
        "delivered": True,
        "pre": ["(en dron1 cliente)", "(estacion-carga cliente)"],
        "eff": ["+ (bateria-alta dron1)"],
    },
    {
        "action": "(volar dron1 cliente base)",
        "drone_pos": "base",
        "battery": False,
        "carrying": False,
        "pkg_pos": "cliente",
        "delivered": True,
        "pre": ["(en dron1 cliente)", "(bateria-alta dron1)"],
        "eff": ["+ (en dron1 base)", "- (en dron1 cliente)", "- (bateria-alta dron1)"],
    },
]

step_idx = 0
drone_x, drone_y = float(LOCATIONS["base"][0]), float(LOCATIONS["base"][1] - 55)
rotor_angle = 0.0
pulse = 0.0


def draw_dashed_line(surface, color, start, end, dash_len=10):
    x1, y1 = start
    x2, y2 = end
    dist = math.hypot(x2 - x1, y2 - y1)
    dashes = int(dist // dash_len)
    for i in range(0, dashes, 2):
        t1 = i / dashes
        t2 = min((i + 1) / dashes, 1.0)
        p1 = (x1 + (x2 - x1) * t1, y1 + (y2 - y1) * t1)
        p2 = (x1 + (x2 - x1) * t2, y1 + (y2 - y1) * t2)
        pygame.draw.line(surface, color, p1, p2, 2)


def draw_package(surface, x, y, delivered=False):
    rect = pygame.Rect(int(x - 16), int(y - 14), 32, 28)
    pygame.draw.rect(surface, AMBER, rect, border_radius=5)
    pygame.draw.rect(surface, (180, 120, 10), rect, 2, border_radius=5)
    pygame.draw.line(surface, (180, 120, 10), (rect.left, rect.centery), (rect.right, rect.centery), 2)
    pygame.draw.line(surface, (180, 120, 10), (rect.centerx, rect.top), (rect.centerx, rect.bottom), 2)
    label = FONT_MONO.render("paq1", True, WHITE)
    surface.blit(label, (rect.centerx - label.get_width() // 2, rect.bottom + 4))
    if delivered:
        badge = FONT_SUB.render("ENTREGADO", True, GREEN)
        surface.blit(badge, (rect.centerx - badge.get_width() // 2, rect.bottom + 22))


def draw_drone(surface, x, y, battery_high, carrying, charging, angle, pulse_val):
    ix, iy = int(x), int(y)

    # Efecto visual de recarga
    if charging:
        r = 42 + int(math.sin(pulse_val) * 8)
        pygame.draw.circle(surface, GREEN, (ix, iy), r, 3)

    # Brazos del dron
    arms = [(-26, -14), (26, -14), (-26, 14), (26, 14)]
    for ax, ay in arms:
        pygame.draw.line(surface, MUTED, (ix, iy), (ix + ax, iy + ay), 4)
        # Rotores girando
        rx, ry = ix + ax, iy + ay
        pygame.draw.circle(surface, (71, 85, 105), (rx, ry), 11, 2)
        dx = math.cos(angle) * 10
        dy = math.sin(angle) * 4
        pygame.draw.line(surface, BLUE, (rx - dx, ry - dy), (rx + dx, ry + dy), 2)

    # Cuerpo central
    body = pygame.Rect(ix - 20, iy - 12, 40, 24)
    pygame.draw.rect(surface, (51, 65, 85), body, border_radius=8)
    pygame.draw.rect(surface, BLUE, body, 2, border_radius=8)

    # LED de estado de batería en el cuerpo
    led_color = GREEN if battery_high else RED
    pygame.draw.circle(surface, led_color, (ix, iy), 5)

    # Barra de batería encima del dron
    bar_w, bar_h = 46, 10
    bar_rect = pygame.Rect(ix - bar_w // 2, iy - 34, bar_w, bar_h)
    pygame.draw.rect(surface, CARD_BG, bar_rect, border_radius=3)
    fill_w = bar_w - 4 if battery_high else 10
    pygame.draw.rect(surface, led_color, (bar_rect.x + 2, bar_rect.y + 2, fill_w, bar_h - 4), border_radius=2)
    pygame.draw.rect(surface, WHITE, bar_rect, 1, border_radius=3)

    # Etiqueta del dron
    lbl = FONT_MONO_BOLD.render("dron1", True, WHITE)
    surface.blit(lbl, (ix - lbl.get_width() // 2, iy - 54))

    # Paquete colgando si lo lleva
    if carrying:
        pygame.draw.line(surface, MUTED, (ix, iy + 12), (ix, iy + 24), 2)
        draw_package(surface, ix, iy + 36, delivered=False)


def draw_panel(surface, idx, step):
    pygame.draw.rect(surface, PANEL_BG, (PANEL_X, 0, WIDTH - PANEL_X, HEIGHT))
    pygame.draw.line(surface, BORDER, (PANEL_X, 0), (PANEL_X, HEIGHT), 2)

    x = PANEL_X + 20
    y = 20

    # Encabezado de paso
    step_title = f"Paso {idx} / {len(STEPS) - 1}"
    surface.blit(FONT_TITLE.render(step_title, True, BLUE), (x, y))
    y += 34

    # Tarjeta de acción actual
    card = pygame.Rect(x, y, WIDTH - PANEL_X - 40, 44)
    pygame.draw.rect(surface, CARD_BG, card, border_radius=8)
    pygame.draw.rect(surface, BLUE, card, 1, border_radius=8)
    surface.blit(FONT_MONO_BOLD.render(step["action"], True, WHITE), (x + 12, y + 13))
    y += 62

    # Precondiciones
    surface.blit(FONT_SUB.render("Precondiciones (:precondition)", True, PURPLE), (x, y))
    y += 26
    for p in step["pre"]:
        surface.blit(FONT_MONO.render(f"• {p}", True, WHITE), (x + 8, y))
        y += 22
    y += 14

    # Efectos
    surface.blit(FONT_SUB.render("Efectos (:effect)", True, AMBER), (x, y))
    y += 26
    for e in step["eff"]:
        col = GREEN if e.startswith("+") else RED if e.startswith("-") else MUTED
        surface.blit(FONT_MONO.render(e, True, col), (x + 8, y))
        y += 22
    y += 18

    # Estado actual del mundo
    surface.blit(FONT_SUB.render("Estado actual", True, WHITE), (x, y))
    y += 26
    bat_txt = "ALTA (lista para volar)" if step["battery"] else "BAJA (requiere recarga)"
    bat_col = GREEN if step["battery"] else RED
    estado_lines = [
        (f"Ubicación: {step['drone_pos']}", WHITE),
        (f"Batería:   {bat_txt}", bat_col),
        (f"Carga:     {'llevando paq1' if step['carrying'] else 'libre'}", WHITE),
    ]
    for txt, col in estado_lines:
        surface.blit(FONT_MONO.render(txt, True, col), (x + 8, y))
        y += 22
    y += 18

    # Metas (:goal)
    surface.blit(FONT_SUB.render("Metas (:goal)", True, GREEN), (x, y))
    y += 26
    goal_delivered = step["delivered"]
    goal_base = step["drone_pos"] == "base" and idx == len(STEPS) - 1
    goals = [
        ("(entregado paq1)", goal_delivered),
        ("(en dron1 base)", goal_base),
    ]
    for g_txt, ok in goals:
        mark = "[OK]" if ok else "[  ]"
        col = GREEN if ok else MUTED
        surface.blit(FONT_MONO_BOLD.render(f"{mark} {g_txt}", True, col), (x + 8, y))
        y += 24

    if goal_delivered and goal_base:
        y += 10
        banner = pygame.Rect(x, y, WIDTH - PANEL_X - 40, 38)
        pygame.draw.rect(surface, (20, 83, 45), banner, border_radius=8)
        pygame.draw.rect(surface, GREEN, banner, 2, border_radius=8)
        msg = FONT_SUB.render("PLAN COMPLETADO CON ÉXITO", True, GREEN)
        surface.blit(msg, (banner.centerx - msg.get_width() // 2, banner.y + 9))


# Bucle principal
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RIGHT, pygame.K_SPACE):
                step_idx = min(step_idx + 1, len(STEPS) - 1)
            elif event.key == pygame.K_LEFT:
                step_idx = max(step_idx - 1, 0)
            elif event.key == pygame.K_r:
                step_idx = 0
            elif event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

    step = STEPS[step_idx]
    target_x, target_y = LOCATIONS[step["drone_pos"]]
    target_y -= 58  # El dron flota encima de la plataforma

    # Interpolación suave del vuelo
    drone_x += (target_x - drone_x) * 0.10
    drone_y += (target_y - drone_y) * 0.10
    rotor_angle += 0.35
    pulse += 0.12

    # Dibujar fondo y título
    screen.fill(BG)
    title = FONT_TITLE.render("Dominio PDDL: dron-entregas", True, WHITE)
    screen.blit(title, (28, 22))
    subtitle = FONT_TEXT.render("Problema: entrega-urbana-1  |  Plan óptimo de 7 pasos", True, MUTED)
    screen.blit(subtitle, (28, 52))

    # Rutas punteadas entre ubicaciones
    draw_dashed_line(screen, BORDER, LOCATIONS["base"], LOCATIONS["almacen"])
    draw_dashed_line(screen, BORDER, LOCATIONS["almacen"], LOCATIONS["cliente"])
    draw_dashed_line(screen, BORDER, LOCATIONS["cliente"], LOCATIONS["base"])

    # Dibujar plataformas de ubicaciones
    for name, (lx, ly) in LOCATIONS.items():
        pad = pygame.Rect(lx - 72, ly - 24, 144, 52)
        active = step["drone_pos"] == name
        pygame.draw.rect(surface=screen, color=CARD_BG, rect=pad, border_radius=12)
        pygame.draw.rect(screen, BLUE if active else BORDER, pad, 2, border_radius=12)

        lbl = FONT_SUB.render(name.upper(), True, WHITE)
        screen.blit(lbl, (lx - lbl.get_width() // 2, ly - 14))

        chg = FONT_TEXT.render("Estación de carga", True, GREEN)
        screen.blit(chg, (lx - chg.get_width() // 2, ly + 8))

    # Dibujar paquete si no lo lleva el dron
    if step["pkg_pos"] is not None:
        px, py = LOCATIONS[step["pkg_pos"]]
        draw_package(screen, px, py + 58, delivered=step["delivered"])

    # Dibujar dron
    is_charging = step["action"].startswith("(recargar")
    draw_drone(screen, drone_x, drone_y, step["battery"], step["carrying"], is_charging, rotor_angle, pulse)

    # Barra inferior de controles
    controls = FONT_TEXT.render("[ESPACIO / →] Siguiente paso    [←] Paso anterior    [R] Reiniciar", True, MUTED)
    screen.blit(controls, (28, HEIGHT - 34))

    # Panel derecho
    draw_panel(screen, step_idx, step)

    pygame.display.flip()
    clock.tick(60)