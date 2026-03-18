import pygame
import sys
import os
import random
import json

# --- PŘIDÁNO: Propojení s databázovým managerem ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Go up one directory (..) to reach the root, then into database_local
sys.path.append(os.path.join(BASE_DIR, "..", "database_local"))
try:
    from db_manager_local import save_game_result
except ImportError as e:
    print(f"❌ Napojení na DB selhalo: {e}")
    save_game_result = None
# --------------------------------------------------

"""
Mancala Game - Maturitní projekt
Tento skript implementuje logiku hry Mancala s grafickým rozhraním v Pygame,
včetně ukládání nastavení do souboru JSON.
"""

# ==============================
#  ČÁST 1 — NASTAVENÍ / TEXTURY
# ==============================

CONFIG_FILE = "settings.json"

def load_settings():
    """
    Načte uživatelské nastavení ze souboru JSON.
    """
    config_path = os.path.join(BASE_DIR, CONFIG_FILE)
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                return json.load(f)
        except:
            pass
    return {"windowed_mode": True}

def save_settings(settings):
    """
    Uloží aktuální konfiguraci aplikace do externího souboru JSON.
    """
    config_path = os.path.join(BASE_DIR, CONFIG_FILE)
    with open(config_path, "w") as f:
        json.dump(settings, f)

# Inicializace nastavení při spuštění aplikace
user_settings = load_settings()

ASSETS_PATH = os.path.dirname(__file__)
WIDTH, HEIGHT = 1280, 720

pygame.init()
font = pygame.font.SysFont("arial", 24)
MENU_FONT = pygame.font.SysFont("arial", 48)

SEED_COLORS = [(210, 180, 140), (139, 69, 19), (222, 184, 135), (101, 67, 33)]

try:
    background_texture = pygame.image.load(os.path.join(ASSETS_PATH, "wood_background.jpg"))
    hole_texture = pygame.image.load(os.path.join(ASSETS_PATH, "wood_dark.jpg"))
except:
    background_texture = None
    hole_texture = None

# ==============================
#  ČÁST 2 — HERNÍ LOGIKA
# ==============================

# --- Dynamická konfigurace ---
PITS_PER_SIDE = 7
SEEDS_PER_PIT = 4

def total_holes():
    return PITS_PER_SIDE * 2 + 2

def index_p1_mancala():
    return PITS_PER_SIDE

def index_p2_mancala():
    return 2 * PITS_PER_SIDE + 1

def p1_pit_indices():
    return list(range(0, PITS_PER_SIDE))

def p2_pit_indices():
    return list(range(PITS_PER_SIDE + 1, 2 * PITS_PER_SIDE + 1))

def is_p1_pit(index):
    return 0 <= index < PITS_PER_SIDE

def is_p2_pit(index):
    return PITS_PER_SIDE + 1 <= index < 2 * PITS_PER_SIDE + 1

def own_mancala(player):
    return index_p1_mancala() if player == 0 else index_p2_mancala()

def opponent_mancala(player):
    return index_p2_mancala() if player == 0 else index_p1_mancala()

def opposite_pit(index):
    # antiparallel across board excluding mancalas
    return 2 * PITS_PER_SIDE - index

board = [SEEDS_PER_PIT] * PITS_PER_SIDE + [0] + [SEEDS_PER_PIT] * PITS_PER_SIDE + [0]
current_player = 0
game_over = False
db_updated = False # PŘIDÁNO: Aby se do DB zapsalo jen jednou za hru

# --- PŘIDÁNO: Proměnné pro jména ---
player1_name = ""
player2_name = ""
active_input = 1 # 1 pro Player 1, 2 pro Player 2

def reset_game():
    """
    Uvede hru do původního stavu. Resetuje herní desku, počítadlo tahů a stav ukončení.
    """
    global board, current_player, game_over, db_updated
    board = [SEEDS_PER_PIT] * PITS_PER_SIDE + [0] + [SEEDS_PER_PIT] * PITS_PER_SIDE + [0]
    current_player = 0
    game_over = False
    db_updated = False # PŘIDÁNO: Reset příznaku uložení

def make_move(start_index):
    """
    Provede kompletní herní tah včetně rozsévání semen a kontroly speciálních pravidel.
    """
    global current_player, board, game_over
    stones = board[start_index]
    if stones == 0: return
    board[start_index] = 0

    current_pos = start_index
    while stones > 0:
        current_pos = (current_pos + 1) % total_holes()
        # Pravidlo: Vynechání soupeřovy pokladnice
        if current_pos == opponent_mancala(current_player):
            continue
        board[current_pos] += 1
        stones -= 1

    # Pravidlo: Zajetí semen (Capture)
    if board[current_pos] == 1:
        if current_player == 0 and is_p1_pit(current_pos):
            opposite = opposite_pit(current_pos)
            if board[opposite] > 0:
                board[own_mancala(0)] += board[opposite] + board[current_pos]
                board[opposite] = 0
                board[current_pos] = 0
        elif current_player == 1 and is_p2_pit(current_pos):
            opposite = opposite_pit(current_pos)
            if board[opposite] > 0:
                board[own_mancala(1)] += board[opposite] + board[current_pos]
                board[opposite] = 0
                board[current_pos] = 0

    check_end_game()

    # Pravidlo: Tah navíc (pokud poslední semeno skončí ve vlastní pokladnici)
    if current_pos == own_mancala(current_player):
        return

    current_player = 1 - current_player

def check_end_game():
    """
    Kontroluje, zda jsou splněny podmínky pro ukončení hry.
    """
    global board, game_over, db_updated
    if sum(board[i] for i in p1_pit_indices()) == 0 or sum(board[i] for i in p2_pit_indices()) == 0:
        board[own_mancala(0)] += sum(board[i] for i in p1_pit_indices())
        board[own_mancala(1)] += sum(board[i] for i in p2_pit_indices())
        for i in p1_pit_indices():
            board[i] = 0
        for i in p2_pit_indices():
            board[i] = 0
        game_over = True

        # --- PŘIDÁNO: Zápis skutečných jmen do DB ---
        if not db_updated and save_game_result:
            save_game_result(player1_name, board[own_mancala(0)], player2_name, board[own_mancala(1)])
            db_updated = True
            print(f"💾 Výsledek uložen do DB: {player1_name} vs {player2_name}")

# ==============================
#  ČÁST 3 — GRAFIKA A VYKRESLOVÁNÍ
# ==============================

def draw_seeds(screen, count, center_x, center_y, radius=30):
    """
    Vykreslí jednotlivá semena do důlku.
    """
    random.seed(count + center_x + center_y) 
    for _ in range(count):
        off_x = random.randint(-radius, radius)
        off_y = random.randint(-radius, radius)
        color = random.choice(SEED_COLORS)
        pygame.draw.circle(screen, color, (center_x + off_x, center_y + off_y), 7)
        pygame.draw.circle(screen, (20, 20, 20), (center_x + off_x, center_y + off_y), 7, 1)

# --- PŘIDÁNO: Funkce pro obrazovku jmen ---
def draw_name_input(screen):
    screen.fill((30, 30, 30))
    draw_text_center(screen, "ZADEJTE JMÉNA HRÁČŮ", 100, (255, 215, 0))
    c1 = (255, 255, 255) if active_input == 1 else (100, 100, 100)
    c2 = (255, 255, 255) if active_input == 2 else (100, 100, 100)
    draw_text_center(screen, f"Hráč 1 (Dole): {player1_name}{'|' if active_input == 1 else ''}", 250, c1)
    draw_text_center(screen, f"Hráč 2 (Nahoře): {player2_name}{'|' if active_input == 2 else ''}", 350, c2)
    if player1_name.strip() and player2_name.strip():
        draw_text_center(screen, "Stiskni ENTER pro start", 500, (0, 255, 0))

def draw_board(screen):
    """
    Vykreslí herní desku.
    """
    w, h = screen.get_size()
    if background_texture:
        screen.blit(pygame.transform.scale(background_texture, (w, h)), (0, 0))
    else:
        screen.fill((180, 140, 100))

    cx = w // 2
    pit_size = min(90, max(50, (w - 400) // PITS_PER_SIDE))
    spacing = pit_size + 30
    p2_y = h // 2 - pit_size - 20
    p1_y = h // 2 + 20
    start_x = cx - (PITS_PER_SIDE - 1) * spacing / 2

    # Vykreslení důlků pro hráče
    for i in range(PITS_PER_SIDE):
        x = int(start_x + i * spacing)
        # dolní řada = hráč 1
        idx_p1 = i
        # horní řada = hráč 2 (reverzní orientace)
        idx_p2 = 2 * PITS_PER_SIDE - i

        for y_off, idx in [(p1_y, idx_p1), (p2_y, idx_p2)]:
            if hole_texture:
                screen.blit(pygame.transform.scale(hole_texture, (pit_size, pit_size)), (x, y_off))
            else:
                pygame.draw.ellipse(screen, (100, 70, 40), (x, y_off, pit_size, pit_size))

            draw_seeds(screen, board[idx], x + pit_size // 2, y_off + pit_size // 2, radius=int(pit_size * 0.3))
            num = font.render(str(board[idx]), True, (255, 255, 255))
            screen.blit(num, (x + pit_size // 2 - num.get_width() // 2, y_off + pit_size // 2 - num.get_height() // 2))

    # Vykreslení pokladnic (Mancaly)
    mancala_width = pit_size
    mancala_height = pit_size * 2 + 20
    p1_mancala_x = int(start_x + PITS_PER_SIDE * spacing)
    p2_mancala_x = int(start_x - spacing)
    mancala_y = h // 2 - mancala_height // 2

    for x, idx in [(p1_mancala_x, index_p1_mancala()), (p2_mancala_x, index_p2_mancala())]:
        pygame.draw.rect(screen, (80, 50, 30), (x, mancala_y, mancala_width, mancala_height), border_radius=20)
        pygame.draw.rect(screen, (40, 25, 15), (x, mancala_y, mancala_width, mancala_height), 3, border_radius=20)
        draw_seeds(screen, board[idx], x + mancala_width // 2, mancala_y + mancala_height // 2, radius=int(mancala_width * 0.25))

    # --- Zobrazení jmen u pokladnic ---
    p1_label = font.render(f"{player1_name}: {board[index_p1_mancala()]}", True, (255, 255, 255))
    p2_label = font.render(f"{player2_name}: {board[index_p2_mancala()]}", True, (255, 255, 255))
    screen.blit(p1_label, (p1_mancala_x, mancala_y + mancala_height + 10))
    screen.blit(p2_label, (p2_mancala_x, mancala_y + mancala_height + 10))

    # Stavové texty
    if not game_over:
        status = player1_name if current_player == 0 else player2_name
        color = (50, 100, 255) if current_player == 0 else (255, 80, 80)
        t = font.render(f"Na tahu: {status}", True, color)
        screen.blit(t, (cx - t.get_width() // 2, 40))
    else:
        if board[index_p1_mancala()] > board[index_p2_mancala()]: res = f"{player1_name} vyhrál!"
        elif board[index_p2_mancala()] > board[index_p1_mancala()]: res = f"{player2_name} vyhrál!"
        else: res = "Remíza!"
        t = MENU_FONT.render(res, True, (255, 215, 0))
        screen.blit(t, (cx - t.get_width() // 2, 30))
        guide = font.render("ESC pro menu", True, (200, 200, 200))
        screen.blit(guide, (cx - guide.get_width() // 2, h - 50))

# ==============================
#  ČÁST 4 — HLAVNÍ SMYČKA A MENU
# ==============================

def draw_text_center(screen, text, y, color=(240, 240, 240)):
    t = MENU_FONT.render(text, True, color)
    screen.blit(t, (screen.get_width() // 2 - t.get_width() // 2, y))

def index_from_click(pos, screen):
    w, h = screen.get_size()
    cx, mx, my = w // 2, pos[0], pos[1]
    pit_size = min(90, max(50, (w - 400) // PITS_PER_SIDE))
    spacing = pit_size + 30
    p2_y = h // 2 - pit_size - 20
    p1_y = h // 2 + 20
    start_x = cx - (PITS_PER_SIDE - 1) * spacing / 2

    for i in range(PITS_PER_SIDE):
        x = int(start_x + i * spacing)
        # spodní řada
        if p1_y <= my <= p1_y + pit_size and x <= mx <= x + pit_size:
            return i
        # horní řada (p2 reversed)
        if p2_y <= my <= p2_y + pit_size and x <= mx <= x + pit_size:
            return 2 * PITS_PER_SIDE - i
    return None

state = "MENU"
windowed_mode = user_settings["windowed_mode"]
apply_mode = True
screen = None
clock = pygame.time.Clock()

# Hlavní smyčka aplikace
while True:
    if apply_mode:
        if windowed_mode: screen = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
        else: screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        
        user_settings["windowed_mode"] = windowed_mode
        save_settings(user_settings)
        apply_mode = False
    
    mx, my = pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        
        # --- PŘIDÁNO: Ovládání vstupu jmen ---
        if state == "NAME_INPUT" and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if active_input == 1 and player1_name.strip(): active_input = 2
                elif active_input == 2 and player2_name.strip(): 
                    state = "GAME"
                    reset_game()
            elif event.key == pygame.K_BACKSPACE:
                if active_input == 1: player1_name = player1_name[:-1]
                else: player2_name = player2_name[:-1]
            elif event.key == pygame.K_ESCAPE: state = "MENU"
            else:
                if len(player1_name if active_input == 1 else player2_name) < 12:
                    if event.unicode.isalnum() or event.unicode == " ":
                        if active_input == 1: player1_name += event.unicode
                        else: player2_name += event.unicode

        if event.type == pygame.KEYDOWN:
            if state == "SETTINGS":
                if event.key == pygame.K_RETURN: 
                    windowed_mode = not windowed_mode
                    apply_mode = True
                if event.key == pygame.K_ESCAPE: state = "MENU"
            elif state == "GAME" and event.key == pygame.K_ESCAPE: state = "MENU"

        if event.type == pygame.MOUSEBUTTONDOWN:
            if state == "MENU":
                h_mid = screen.get_height() // 2
                if h_mid - 80 < my < h_mid - 20: 
                    # --- UPRAVENO: Místo resetu jdeme na zadání jmen ---
                    player1_name = ""; player2_name = ""; active_input = 1
                    state = "NAME_INPUT"
                elif h_mid < my < h_mid + 50: state = "SETTINGS"
                elif h_mid + 60 < my < h_mid + 140: pygame.quit(); sys.exit()
            elif state == "GAME" and not game_over:
                idx = index_from_click((mx, my), screen)
                if idx is not None:
                    if (current_player == 0 and is_p1_pit(idx)) or (current_player == 1 and is_p2_pit(idx)):
                        make_move(idx)

    # Vykreslování podle stavu aplikace
    if state == "NAME_INPUT":
        draw_name_input(screen)
    elif state == "MENU":
        screen.fill((40, 40, 40))
        draw_text_center(screen, "HRÁT", screen.get_height() // 2 - 60)
        draw_text_center(screen, "NASTAVENÍ", screen.get_height() // 2)
        draw_text_center(screen, "KONEC", screen.get_height() // 2 + 60)
    elif state == "SETTINGS":
        screen.fill((30, 30, 30))
        txt = "Windowed" if windowed_mode else "Fullscreen"
        draw_text_center(screen, f"Režim: {txt}", screen.get_height() // 2 - 20)
        draw_text_center(screen, "Enter: Přepnout | Esc: Zpět", screen.get_height() // 2 + 60, (150, 150, 150))
    elif state == "GAME":
        draw_board(screen)

    pygame.display.flip()
    clock.tick(60)