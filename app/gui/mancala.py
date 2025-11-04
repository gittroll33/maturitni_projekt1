import pygame
import sys
import os

# ==============================
# 🔹 ČÁST 1 — NAČÍTÁNÍ TEXTUR
# ==============================

ASSETS_PATH = os.path.join(os.path.dirname(__file__), "assets")

WIDTH, HEIGHT = 900, 400
TEXT_COLOR = (30, 20, 10)

pygame.init()
font = pygame.font.SysFont("arial", 28)
MENU_FONT = pygame.font.SysFont("arial", 48)

# --- Načtení textur s kontrolou ---
try:
    background_texture = pygame.image.load(os.path.join(ASSETS_PATH, "wood_background.jpg"))
    hole_texture = pygame.image.load(os.path.join(ASSETS_PATH, "wood_dark.jpg"))
    print("✅ Textury úspěšně načteny.")
except Exception as e:
    print("⚠️ Chyba při načítání textur:", e)
    background_texture = None
    hole_texture = None

if background_texture:
    background_texture = pygame.transform.scale(background_texture, (WIDTH, HEIGHT))
if hole_texture:
    hole_texture = pygame.transform.scale(hole_texture, (90, 90))


# ==============================
# 🔹 ČÁST 2 — VYKRESLENÍ HRACÍ DESKY
# ==============================

def draw_board(screen):
    if background_texture:
        bg = pygame.transform.scale(background_texture, screen.get_size())
        screen.blit(bg, (0, 0))
    else:
        screen.fill((180, 140, 100))

    width, height = screen.get_size()
    cx = width // 2

    for i in range(6):
        x = cx - 350 + i * 120
        y_top = height // 2 - 120
        y_bottom = height // 2 + 30

        if hole_texture:
            hole = pygame.transform.scale(hole_texture, (90, 90))
            screen.blit(hole, (x, y_top))
            screen.blit(hole, (x, y_bottom))
        else:
            pygame.draw.ellipse(screen, (100, 70, 40), (x, y_top, 90, 90))
            pygame.draw.ellipse(screen, (100, 70, 40), (x, y_bottom, 90, 90))

    pygame.draw.rect(screen, (80, 50, 30), (cx - 460, height // 2 - 90, 60, 180), border_radius=20)
    pygame.draw.rect(screen, (80, 50, 30), (cx + 400, height // 2 - 90, 60, 180), border_radius=20)

    title = font.render("MANCALA", True, TEXT_COLOR)
    screen.blit(title, (cx - title.get_width() // 2, 30))


# ==============================
# 🔹 ČÁST 3 — MENU / SETTINGS
# ==============================

state = "MENU"
windowed_mode = True

def apply_window_mode():
    global screen
    if windowed_mode:
        screen = pygame.display.set_mode((1280, 720), pygame.RESIZABLE | pygame.WINDOWMAXIMIZED)
    else:
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.display.set_caption("Mancala — Hra")

apply_window_mode()


def draw_text_center(text, y):
    t = MENU_FONT.render(text, True, (240, 240, 240))
    screen.blit(t, (screen.get_width() // 2 - t.get_width() // 2, y))


def menu():
    screen.fill((40, 40, 40))
    draw_text_center("Hrát", screen.get_height() // 2 - 60)
    draw_text_center("Nastavení", screen.get_height() // 2)
    draw_text_center("Konec", screen.get_height() // 2 + 60)


def settings():
    screen.fill((30, 30, 30))
    mode = "Windowed" if windowed_mode else "Fullscreen"
    draw_text_center(f"Režim: {mode}", screen.get_height() // 2 - 20)
    draw_text_center(f"Enter: Přepnout", screen.get_height() // 2 + 40)
    draw_text_center(f"Esc:  Zpět", screen.get_height() // 2 + 100)


# ==============================
# 🔹 ČÁST 4 — HLAVNÍ SMYČKA
# ==============================

clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if state == "MENU":
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                h = screen.get_height() // 2
                if h - 80 < y < h - 20: state = "GAME"
                elif h + 0 < y < h + 50: state = "SETTINGS"
                elif h + 60 < y < h + 120: pygame.quit(); sys.exit()

        elif state == "SETTINGS":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    windowed_mode = not windowed_mode
                    apply_window_mode()
                if event.key == pygame.K_ESCAPE:
                    state = "MENU"

        elif state == "GAME":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                state = "MENU"

    if state == "MENU":
        menu()
    elif state == "SETTINGS":
        settings()
    elif state == "GAME":
        draw_board(screen)

    pygame.display.flip()
    clock.tick(60)
