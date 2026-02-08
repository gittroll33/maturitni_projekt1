import pygame
import sys
import os
import random
import json

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
    
    Returns:
        dict: Slovník s uloženým nastavením. Pokud soubor neexistuje nebo je poškozen,
              vrátí výchozí hodnoty (windowed_mode: True).
    """
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    return {"windowed_mode": True}

def save_settings(settings):
    """
    Uloží aktuální konfiguraci aplikace do externího souboru JSON.
    
    Args:
        settings (dict): Slovník obsahující data k uložení (např. režim zobrazení).
    """
    with open(CONFIG_FILE, "w") as f:
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

# Inicializace desky: 0-5 (hráč dole), 6 (pokladnice dole), 7-12 (hráč nahoře), 13 (pokladnice nahoře)
board = [4, 4, 4, 4, 4, 4, 0, 4, 4, 4, 4, 4, 4, 0]
current_player = 0 
game_over = False

def reset_game():
    """
    Uvede hru do původního stavu. Resetuje herní desku, počítadlo tahů a stav ukončení.
    """
    global board, current_player, game_over
    board = [4, 4, 4, 4, 4, 4, 0, 4, 4, 4, 4, 4, 4, 0]
    current_player = 0
    game_over = False

def make_move(start_index):
    """
    Provede kompletní herní tah včetně rozsévání semen a kontroly speciálních pravidel.
    
    Args:
        start_index (int): Index důlku, ze kterého hráč začíná rozesévat semena.
    """
    global current_player, board, game_over
    stones = board[start_index]
    if stones == 0: return 
    board[start_index] = 0
    
    current_pos = start_index
    while stones > 0:
        current_pos = (current_pos + 1) % 14
        # Pravidlo: Vynechání soupeřovy pokladnice
        if current_player == 0 and current_pos == 13: continue
        if current_player == 1 and current_pos == 6: continue
        board[current_pos] += 1
        stones -= 1

    # Pravidlo: Zajetí semen (Capture)
    if board[current_pos] == 1:
        if current_player == 0 and 0 <= current_pos <= 5:
            opposite = 12 - current_pos
            if board[opposite] > 0:
                board[6] += board[opposite] + board[current_pos]
                board[opposite] = 0
                board[current_pos] = 0
        elif current_player == 1 and 7 <= current_pos <= 12:
            opposite = 12 - current_pos
            if board[opposite] > 0:
                board[13] += board[opposite] + board[current_pos]
                board[opposite] = 0
                board[current_pos] = 0

    check_end_game()
    
    # Pravidlo: Tah navíc (pokud poslední semeno skončí ve vlastní pokladnici)
    if (current_player == 0 and current_pos == 6) or (current_player == 1 and current_pos == 13):
        return 
    current_player = 1 - current_player

def check_end_game():
    """
    Kontroluje, zda jsou splněny podmínky pro ukončení hry (jedna strana je prázdná).
    Pokud ano, přesune zbývající semena do pokladnic a ukončí hru.
    """
    global board, game_over
    if sum(board[0:6]) == 0 or sum(board[7:13]) == 0:
        board[6] += sum(board[0:6])
        board[13] += sum(board[7:13])
        for i in range(6):
            board[i] = 0
            board[i+7] = 0
        game_over = True

# ==============================
#  ČÁST 3 — GRAFIKA A VYKRESLOVÁNÍ
# ==============================

def draw_seeds(screen, count, center_x, center_y, radius=30):
    """
    Vykreslí jednotlivá semena (kuličky) do důlku s náhodným rozptylem pro realističtější vzhled.
    
    Args:
        screen (pygame.Surface): Plocha, na kterou se vykresluje.
        count (int): Počet semen k vykreslení.
        center_x (int): X souřadnice středu důlku.
        center_y (int): Y souřadnice středu důlku.
        radius (int): Maximální vzdálenost kuličky od středu důlku.
    """
    random.seed(count + center_x + center_y) 
    for _ in range(count):
        off_x = random.randint(-radius, radius)
        off_y = random.randint(-radius, radius)
        color = random.choice(SEED_COLORS)
        pygame.draw.circle(screen, color, (center_x + off_x, center_y + off_y), 7)
        pygame.draw.circle(screen, (20, 20, 20), (center_x + off_x, center_y + off_y), 7, 1)

def draw_board(screen):
    """
    Vykreslí herní desku, důlky, pokladnice, semena a aktuální stav hry (kdo je na tahu / vítěz).
    
    Args:
        screen (pygame.Surface): Plocha, na kterou se vykresluje.
    """
    w, h = screen.get_size()
    if background_texture:
        screen.blit(pygame.transform.scale(background_texture, (w, h)), (0, 0))
    else:
        screen.fill((180, 140, 100))
    
    cx = w // 2
    # Vykreslení 6 důlků pro každého hráče
    for i in range(6):
        x = cx - 350 + i * 120
        for y_off, idx in [(h//2 + 30, i), (h//2 - 120, 12-i)]:
            if hole_texture:
                screen.blit(pygame.transform.scale(hole_texture, (90, 90)), (x, y_off))
            else:
                pygame.draw.ellipse(screen, (100, 70, 40), (x, y_off, 90, 90))
            
            draw_seeds(screen, board[idx], x + 45, y_off + 45)
            num = font.render(str(board[idx]), True, (255, 255, 255))
            screen.blit(num, (x + 35, y_off + 65))

    # Vykreslení pokladnic (Mancaly)
    pygame.draw.rect(screen, (80, 50, 30), (cx + 390, h // 2 - 90, 80, 180), border_radius=20)
    pygame.draw.rect(screen, (40, 25, 15), (cx + 390, h // 2 - 90, 80, 180), 3, border_radius=20)
    pygame.draw.rect(screen, (80, 50, 30), (cx - 470, h // 2 - 90, 80, 180), border_radius=20)
    pygame.draw.rect(screen, (40, 25, 15), (cx - 470, h // 2 - 90, 80, 180), 3, border_radius=20)

    draw_seeds(screen, board[6], cx + 430, h // 2, radius=25)
    draw_seeds(screen, board[13], cx - 430, h // 2, radius=25)

    screen.blit(font.render(str(board[6]), True, (255, 255, 255)), (cx + 420, h // 2 + 100))
    screen.blit(font.render(str(board[13]), True, (255, 255, 255)), (cx - 440, h // 2 + 100))

    # Stavové texty (kdo hraje / kdo vyhrál)
    if not game_over:
        status = "Hráč DOLE" if current_player == 0 else "Hráč NAHOŘE"
        color = (50, 100, 255) if current_player == 0 else (255, 80, 80)
        t = font.render(f"Na tahu: {status}", True, color)
        screen.blit(t, (cx - t.get_width() // 2, 40))
    else:
        if board[6] > board[13]: res = "Hráč DOLE vyhrál!"
        elif board[13] > board[6]: res = "Hráč NAHOŘE vyhrál!"
        else: res = "Remíza!"
        t = MENU_FONT.render(res, True, (255, 215, 0))
        screen.blit(t, (cx - t.get_width() // 2, 30))
        guide = font.render("ESC pro menu", True, (200, 200, 200))
        screen.blit(guide, (cx - guide.get_width() // 2, h - 50))

# ==============================
#  ČÁST 4 — HLAVNÍ SMYČKA A MENU
# ==============================

def draw_text_center(screen, text, y, color=(240, 240, 240)):
    """
    Pomocná funkce pro vykreslení vycentrovaného textu na obrazovku.
    """
    t = MENU_FONT.render(text, True, color)
    screen.blit(t, (screen.get_width() // 2 - t.get_width() // 2, y))

def index_from_click(pos, screen):
    """
    Převede souřadnice kliknutí myši na index důlku v poli 'board'.
    
    Args:
        pos (tuple): (x, y) souřadnice kliknutí.
        screen (pygame.Surface): Aktuální plocha okna (pro výpočet středu).
        
    Returns:
        int or None: Index důlku (0-12) nebo None, pokud bylo kliknuto mimo.
    """
    w, h = screen.get_size()
    cx, mx, my = w // 2, pos[0], pos[1]
    for i in range(6):
        x_pos = cx - 350 + i * 120
        if h // 2 + 30 <= my <= h // 2 + 120 and x_pos <= mx <= x_pos + 90: return i
        if h // 2 - 120 <= my <= h // 2 - 30 and x_pos <= mx <= x_pos + 90: return 12 - i
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
        
        # Uložíme nastavení pokud došlo ke změně
        user_settings["windowed_mode"] = windowed_mode
        save_settings(user_settings)
        apply_mode = False
    
    mx, my = pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        
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
                if h_mid - 80 < my < h_mid - 20: reset_game(); state = "GAME"
                elif h_mid < my < h_mid + 50: state = "SETTINGS"
                elif h_mid + 60 < my < h_mid + 140: pygame.quit(); sys.exit()
            elif state == "GAME" and not game_over:
                idx = index_from_click((mx, my), screen)
                if idx is not None:
                    # Kontrola, zda hráč klikl na svou stranu
                    if (current_player == 0 and 0 <= idx <= 5) or (current_player == 1 and 7 <= idx <= 12):
                        make_move(idx)

    # Vykreslování podle stavu aplikace
    if state == "MENU":
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