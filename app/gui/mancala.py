import pygame
import sys
import os

# ==============================
#  ČÁST 1 — NASTAVENÍ / TEXTURY
# ==============================

ASSETS_PATH = os.path.join(os.path.dirname(__file__), "assets")

WIDTH, HEIGHT = 900, 400
TEXT_COLOR = (30, 20, 10)

pygame.init()
font = pygame.font.SysFont("arial", 28)
MENU_FONT = pygame.font.SysFont("arial", 48)

# Načtení textur
try:
    background_texture = pygame.image.load(os.path.join(ASSETS_PATH, "wood_background.jpg"))
    hole_texture = pygame.image.load(os.path.join(ASSETS_PATH, "wood_dark.jpg"))
    print("✅ Textury načteny.")
except:
    background_texture = None
    hole_texture = None
    print("⚠️ Textury nenalezeny, používá se fallback grafika.")

if background_texture:
    background_texture = pygame.transform.scale(background_texture, (WIDTH, HEIGHT))
if hole_texture:
    hole_texture = pygame.transform.scale(hole_texture, (90, 90))

# ==============================
#  ČÁST 2 — HERNÍ LOGIKA
# ==============================

board = [4, 4, 4, 4, 4, 4, 0,
         4, 4, 4, 4, 4, 4, 0]

current_player = 0  # 0 = dole, 1 = nahoře


def index_from_click(pos, screen):
    width, height = screen.get_size()
    cx = width // 2
    mx, my = pos

    for i in range(6):
        x = cx - 350 + i * 120

        if height // 2 - 120 <= my <= height // 2 - 30:
            if x <= mx <= x + 90:
                return i

        if height // 2 + 30 <= my <= height // 2 + 120:
            if x <= mx <= x + 90:
                return 7 + i

    return None


def make_move(start):
    global current_player, board

    stones = board[start]
    if stones == 0:
        return
    board[start] = 0

    i = start
    while stones > 0:
        i = (i + 1) % 14

        if current_player == 0 and i == 6: 
            continue
        if current_player == 1 and i == 13:
            continue

        board[i] += 1
        stones -= 1

    # Capture
    if current_player == 0 and 7 <= i <= 12 and board[i] == 1:
        opposite = 12 - (i - 7)
        board[13] += board[opposite] + 1
        board[i] = board[opposite] = 0

    if current_player == 1 and 0 <= i <= 5 and board[i] == 1:
        opposite = 5 - i
        board[6] += board[opposite] + 1
        board[i] = board[opposite] = 0

    # Bonus move check
    if (current_player == 0 and i == 13) or (current_player == 1 and i == 6):
        return

    current_player = 1 - current_player


# ==============================
#  ČÁST 3 — VYKRESLENÍ PLÁNA
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

        hole = pygame.transform.scale(hole_texture, (90, 90)) if hole_texture else None

        if hole:
            screen.blit(hole, (x, y_top))
            screen.blit(hole, (x, y_bottom))
        else:
            pygame.draw.ellipse(screen, (100, 70, 40), (x, y_top, 90, 90))
            pygame.draw.ellipse(screen, (100, 70, 40), (x, y_bottom, 90, 90))

        screen.blit(font.render(str(board[i]), True, (0, 0, 0)), (x + 35, y_top + 30))
        screen.blit(font.render(str(board[7 + i]), True, (0, 0, 0)), (x + 35, y_bottom + 30))

    pygame.draw.rect(screen, (80, 50, 30), (cx - 460, height // 2 - 90, 60, 180), border_radius=20)
    pygame.draw.rect(screen, (80, 50, 30), (cx + 400, height // 2 - 90, 60, 180), border_radius=20)

    screen.blit(font.render(str(board[6]), True, (0, 0, 0)), (cx - 440, height // 2 - 10))
    screen.blit(font.render(str(board[13]), True, (0, 0, 0)), (cx + 420, height // 2 - 10))

    # ==============================
    # ✅ Indikace hráče
    # ==============================
    if current_player == 0:
        turn_text = font.render("Na tahu: Spodní hráč", True, (20, 60, 200))
    else:
        turn_text = font.render("Na tahu: Horní hráč", True, (200, 50, 50))

    screen.blit(turn_text, (cx - turn_text.get_width() // 2, 20))


# ==============================
#  ČÁST 4 — MENU / SETTINGS
# ==============================

state = "MENU"
windowed_mode = True


def apply_window_mode():
    global screen
    if windowed_mode:
        screen = pygame.display.set_mode((1280, 720), pygame.RESIZABLE | pygame.WINDOWMAXIMIZED)
    else:
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)


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
    draw_text_center("Enter: Přepnout", screen.get_height() // 2 + 40)
    draw_text_center("Esc:  Zpět", screen.get_height() // 2 + 100)


# ==============================
#  ČÁST 5 — HLAVNÍ SMYČKA
# ==============================

clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if state == "MENU":
            if event.type == pygame.MOUSEBUTTONDOWN:
                y = pygame.mouse.get_pos()[1]
                h = screen.get_height() // 2
                if h - 80 < y < h - 20: state = "GAME"
                elif h < y < h + 50: state = "SETTINGS"
                elif h + 60 < y < h + 140: pygame.quit(); sys.exit()

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
            if event.type == pygame.MOUSEBUTTONDOWN:
                clicked = index_from_click(pygame.mouse.get_pos(), screen)
                if clicked is not None:
                    if (current_player == 0 and 7 <= clicked <= 12) or (current_player == 1 and 0 <= clicked <= 5):
                        make_move(clicked)

    if state == "MENU":
        menu()
    elif state == "SETTINGS":
        settings()
    elif state == "GAME":
        draw_board(screen)

    pygame.display.flip()
    clock.tick(60)
