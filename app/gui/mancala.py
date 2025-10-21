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

# --- Načtení textur s kontrolou ---
try:
    background_texture = pygame.image.load(os.path.join(ASSETS_PATH, "wood_background.jpg"))
    hole_texture = pygame.image.load(os.path.join(ASSETS_PATH, "wood_dark.jpg"))
    print("✅ Textury úspěšně načteny.")
except Exception as e:
    print("⚠️ Chyba při načítání textur:", e)
    background_texture = None
    hole_texture = None

# --- Roztáhnutí textur na správnou velikost ---
if background_texture:
    background_texture = pygame.transform.scale(background_texture, (WIDTH, HEIGHT))
if hole_texture:
    hole_texture = pygame.transform.scale(hole_texture, (90, 90))


# ==============================
# 🔹 ČÁST 2 — ZÁKLAD HRY (LOGIKA + VYKRESLENÍ)
# ==============================

def draw_board(screen):
    """Vykreslí hrací plochu"""
    if background_texture:
        screen.blit(background_texture, (0, 0))
    else:
        screen.fill((180, 140, 100))  # fallback barva

    # Nakreslení jamek (zatím jednoduché)
    for i in range(6):
        x = 120 + i * 120
        y_top = 80
        y_bottom = 230

        if hole_texture:
            screen.blit(hole_texture, (x, y_top))
            screen.blit(hole_texture, (x, y_bottom))
        else:
            pygame.draw.ellipse(screen, (100, 70, 40), (x, y_top, 90, 90))
            pygame.draw.ellipse(screen, (100, 70, 40), (x, y_bottom, 90, 90))

    # Domy (velké jamky)
    pygame.draw.rect(screen, (80, 50, 30), (40, 120, 60, 160), border_radius=20)
    pygame.draw.rect(screen, (80, 50, 30), (WIDTH - 100, 120, 60, 160), border_radius=20)

    # Text
    title = font.render("MANCALA — test textur", True, TEXT_COLOR)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 20))


# ==============================
# 🔹 ČÁST 3 — HLAVNÍ SMYČKA HRY
# ==============================

def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Mancala — test grafiky")

    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        draw_board(screen)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
