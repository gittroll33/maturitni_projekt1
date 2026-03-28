import pygame
import sys
import os
import random
import json

# --- Propojení s databázovým managerem ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Jdi o jednu úroveň výš, do složky "database_local" (..), a zkus importovat funkci pro ukládání výsledků
sys.path.append(os.path.join(BASE_DIR, "..", "database_local"))
try:
    from db_manager_local import save_game_result
except ImportError as e:
    print(f"Napojení na DB selhalo: {e}")
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

    Returns:
        dict: Slovník s nastavením (např. {"windowed_mode": bool}). 
              Vrací výchozí hodnoty, pokud soubor neexistuje nebo je poškozen.
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

    Args:
        settings (dict): Slovník obsahující aktuální nastavení k uložení.
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
SEEDS_PER_PIT = 5
MOVE_COUNT = 0
r_clicks = 0
previous_board = None
previous_player = 0
undo_offset_y = 10

def total_holes():
    """
    Vypočítá celkový počet prvků v poli desky (jamky + obě pokladnice).

    Returns:
        int: Celkový počet pozic na herní desce.
    """
    return PITS_PER_SIDE * 2 + 2

def index_p1_mancala():
    """
    Určí index v poli desky, který náleží pokladnici prvního hráče.

    Returns:
        int: Index pokladnice hráče 1.
    """
    return PITS_PER_SIDE

def index_p2_mancala():
    """
    Určí index v poli desky, který náleží pokladnici druhého hráče.

    Returns:
        int: Index pokladnice hráče 2.
    """
    return 2 * PITS_PER_SIDE + 1

def p1_pit_indexes():
    """
    Vytvoří seznam všech indexů jamek, které patří hráči 1 (spodní strana).

    Returns:
        list[int]: Seznam indexů jamek hráče 1.
    """
    return list(range(0, PITS_PER_SIDE))

def p2_pit_indexes():
    """
    Vytvoří seznam všech indexů jamek, které patří hráči 2 (horní strana).

    Returns:
        list[int]: Seznam indexů jamek hráče 2.
    """
    return list(range(PITS_PER_SIDE + 1, 2 * PITS_PER_SIDE + 1))

def is_p1_pit(index):
    """
    Ověří, zda daný index patří do herního pole hráče 1.

    Args:
        index (int): Kontrolovaný index na desce.

    Returns:
        bool: True, pokud index patří hráči 1, jinak False.
    """
    return 0 <= index < PITS_PER_SIDE

def is_p2_pit(index):
    """
    Ověří, zda daný index patří do herního pole hráče 2.

    Args:
        index (int): Kontrolovaný index na desce.

    Returns:
        bool: True, pokud index patří hráči 2, jinak False.
    """
    return PITS_PER_SIDE + 1 <= index < 2 * PITS_PER_SIDE + 1

def own_mancala(player):
    """
    Vrátí index pokladnice aktivního hráče.

    Args:
        player (int): Identifikátor hráče (0 pro Player 1, 1 pro Player 2).

    Returns:
        int: Index vlastní pokladnice.
    """
    return index_p1_mancala() if player == 0 else index_p2_mancala()

def opponent_mancala(player):
    """
    Vrátí index pokladnice soupeře.

    Args:
        player (int): Identifikátor aktivního hráče (0 nebo 1).

    Returns:
        int: Index soupeřovy pokladnice.
    """
    return index_p2_mancala() if player == 0 else index_p1_mancala()

def opposite_pit(index):

    """
    Najde index protilehlé jamky na desce (zrcadlově).
    Používá se pro implementaci pravidla 'Capture'.

    Args:
        index (int): Index jamky, ke které hledáme protějšek.

    Returns:
        int: Index zrcadlově protilehlé jamky.
    """
    return 2 * PITS_PER_SIDE - index

board = [SEEDS_PER_PIT] * PITS_PER_SIDE + [0] + [SEEDS_PER_PIT] * PITS_PER_SIDE + [0]
current_player = 0
game_over = False
db_updated = False # Aby se do DB zapsalo jen jednou za hru

# --- Proměnné pro jména ---
player1_name = ""
player2_name = ""
active_input = 1 # 1 pro Player 1, 2 pro Player 2

def reset_game(): 
    """
    Uvede hru do výchozího stavu. Resetuje kameny v jamkách, 
    vynuluje skóre, počítadlo tahů a stavové příznaky.
    """
    global board, current_player, game_over, db_updated, MOVE_COUNT
    board = [SEEDS_PER_PIT] * PITS_PER_SIDE + [0] + [SEEDS_PER_PIT] * PITS_PER_SIDE + [0]
    current_player = 0
    game_over = False
    db_updated = False # Reset příznaku uložení
    MOVE_COUNT = 0 # Reset počítadla tahů

def make_move(start_index):
    """
    Realizuje herní tah: rozsev semen, ošetření přeskočení soupeřovy pokladnice,
    pravidlo Capture a kontrolu bonusového tahu.

    Args:
        start_index (int): Index jamky, ze které hráč začíná zasévat.
    """
    
    global current_player, board, game_over, MOVE_COUNT, r_clicks, previous_board, previous_player
    # Uložíme si aktuální stav, než ho změníme s použitím .copy()
    previous_board = board.copy()
    # Uložíme si, kdo je na tahu, abychom se mohli vrátit zpět v případě Undo
    previous_player = current_player
    # Zjistíme, kolik kuliček (stones) je v důlku, na který hráč klikl
    stones = board[start_index]
    #Pokud je důlek prázdný, tah nelze provést, proto funkci okamžitě ukončíme
    if stones == 0: return
    # Vyjmeme kuličky z vybraného důlku (nastavíme jeho hodnotu na 0)
    board[start_index] = 0
    # Zvýšíme celkové počítadlo provedených tahů ve hře
    MOVE_COUNT += 1
    r_clicks = 0 # Reset počítadla kliků pro reset po každém tahu

    # Nastavíme si počáteční pozici pro rozesévání na index, ze kterého jsme kuličky vzali
    current_pos = start_index
    while stones > 0:
        # Posuneme se na další důlek v pořadí (modulo '%' zajistí, že po posledním indexu skočíme na 0)
        current_pos = (current_pos + 1) % total_holes()
        # Pravidlo: Vynechání soupeřovy pokladnice
        if current_pos == opponent_mancala(current_player):
            continue
        # Vhodíme jednu kuličku do aktuálního důlku
        board[current_pos] += 1
        # Snížíme počet kuliček, které nám zbývají v ruce
        stones -= 1
        

    # Pravidlo: Zajetí semen (Capture)
    # Kontrolujeme, zda poslední semeno padlo do důlku, který byl předtím prázdný
    if board[current_pos] == 1:
        # LOGIKA PRO HRÁČE 1 (Spodní řada)
        if current_player == 0 and is_p1_pit(current_pos):
            # 1. Najdeme index důlku, který leží přesně naproti našemu důlku
            opposite = opposite_pit(current_pos)
            # 2. Pokud u soupeře naproti něco je, provedeme zajetí
            if board[opposite] > 0:
                # Sebereme soupeřova semena + naše jedno aktivní a dáme je do naší pokladnice
                board[own_mancala(0)] += board[opposite] + board[current_pos]
                # 3. Vyprázdníme oba důlky (přesunuli jsme je do pokladnice)
                board[opposite] = 0
                board[current_pos] = 0
                # LOGIKA PRO HRÁČE 2 (Horní řada)
        elif current_player == 1 and is_p2_pit(current_pos):
            # 1. Najdeme index protilehlého důlku
            opposite = opposite_pit(current_pos)
            # 2. Pokud u soupeře naproti něco je, provedeme zajetí
            if board[opposite] > 0:
                # Sebereme soupeřova semena + naše jedno aktivní a dáme je do naší pokladnice
                board[own_mancala(1)] += board[opposite] + board[current_pos]
                # 3. Vyprázdníme oba důlky
                board[opposite] = 0
                board[current_pos] = 0

    check_end_game()

    # Pravidlo: Tah navíc (pokud poslední semeno skončí ve vlastní pokladnici)
    if current_pos == own_mancala(current_player):
        return

    current_player = 1 - current_player

def check_end_game():
    """
    Provádí kontrolu konce hry (prázdná strana). V případě konce sečte 
    zbývající kameny do pokladnic a zapíše výsledek do databáze.
    """
    # Přístup ke globálním proměnným, abychom je mohli v rámci funkce měnit
    global board, game_over, db_updated
    # KONTROLA: Pokud je součet semen v jamkách Hráče 1 NEBO Hráče 2 roven nule
    if sum(board[i] for i in p1_pit_indexes()) == 0 or sum(board[i] for i in p2_pit_indexes()) == 0:
        # PŘESUN: Sečteme zbylá semena na straně Hráče 1 a přičteme je do jeho pokladnice
        board[own_mancala(0)] += sum(board[i] for i in p1_pit_indexes())
        # PŘESUN: Sečteme zbylá semena na straně Hráče 2 a přičteme je do jeho pokladnice
        board[own_mancala(1)] += sum(board[i] for i in p2_pit_indexes())
        # VYČIŠTĚNÍ: Projdeme všechny indexy jamek Hráče 1 a nastavíme je na 0
        for i in p1_pit_indexes():
            board[i] = 0
        # VYČIŠTĚNÍ: Projdeme všechny indexy jamek Hráče 2 a nastavíme je na 0
        for i in p2_pit_indexes():
            board[i] = 0
        # STAV: Nastavíme příznak konce hry na True, což zastaví možnost dalších tahů
        game_over = True

        # --- Zápis skutečných jmen do DB ---
        if not db_updated and save_game_result:
            save_game_result(player1_name, board[own_mancala(0)], player2_name, board[own_mancala(1)])
            db_updated = True
            print(f"Výsledek uložen do DB: {player1_name} vs {player2_name}")

# ==============================
#  ČÁST 3 — GRAFIKA A VYKRESLOVÁNÍ
# ==============================

def draw_seeds(screen, count, center_x, center_y, radius=30):
    """
    Vykreslí grafickou reprezentaci semen v rámci jednoho důlku 
    s náhodným rozptylem pro realističtější vzhled.

    Args:
        screen (pygame.Surface): Plocha, na kterou se vykresluje.
        count (int): Počet semen k vykreslení.
        center_x (int): X-ová souřadnice středu důlku.
        center_y (int): Y-ová souřadnice středu důlku.
        radius (int, optional): Oblast rozptylu semen. Výchozí je 30.
    """

    # 1. Zafixuje náhodu (seed) podle počtu semen a pozice jamky. 
    #    Díky tomu kuličky v jamce "netančí" při každém překreslení obrazovky, ale leží stále na stejných místech.
    random.seed(count + center_x + center_y) 
    # 2. Cyklus, který se zopakuje tolikrát, kolik je v jamce kuliček (count).
    #    Podtržítko '_' značí, že nás nezajímá pořadové číslo průchodu, jen počet opakování.
    for _ in range(count):
        # 3. Vygeneruje náhodný posun na ose X v rozmezí 'radius' (aby kulička zůstala uvnitř jamky)
        off_x = random.randint(-radius, radius)
        # 4. Vygeneruje náhodný posun na ose Y
        off_y = random.randint(-radius, radius)
        # 5. Vybere náhodnou barvu pro kuličku ze seznamu předdefinovaných barev (SEED_COLORS)
        color = random.choice(SEED_COLORS)
        # 6. Vykreslí vyplněný kruh (kuličku) na vypočítané pozici (střed jamky + náhodný posun)
        pygame.draw.circle(screen, color, (center_x + off_x, center_y + off_y), 7)
        # 7. Vykreslí tenký tmavý obrys kolem kuličky, aby byly od sebe lépe vidět, když se překrývají
        pygame.draw.circle(screen, (20, 20, 20), (center_x + off_x, center_y + off_y), 7, 1)


def draw_name_input(screen):
    """
    Vykreslí rozhraní pro zadávání jmen hráčů včetně grafického 
    zvýraznění aktivního vstupního pole.

    Args:
        screen (pygame.Surface): Plocha pro vykreslení.
    """
    screen.fill((30, 30, 30))
    draw_text_center(screen, "ZADEJTE JMÉNA HRÁČŮ", 100, (255, 215, 0))
    # LOGIKA BAREV: Pokud hráč právě píše do pole 1, barva (c1) bude bílá (255, 255, 255).
    # Pokud ne, barva bude šedá (100, 100, 100), aby bylo vidět, že pole není aktivní.
    c1 = (255, 255, 255) if active_input == 1 else (100, 100, 100)
    c2 = (255, 255, 255) if active_input == 2 else (100, 100, 100)
    # Za jméno přidá znak '|' (kurzor), pokud je pole aktivní, jinak nepřidá nic.
    draw_text_center(screen, f"Hráč 1 (Dole): {player1_name}{'|' if active_input == 1 else ''}", 250, c1)
    draw_text_center(screen, f"Hráč 2 (Nahoře): {player2_name}{'|' if active_input == 2 else ''}", 350, c2)
    # Pokud obě jména obsahují aspoň jeden znak (nejsou prázdná), zobrazí se nápověda pro start.
    if player1_name.strip() and player2_name.strip():
        draw_text_center(screen, "Stiskni ENTER pro start", 500, (0, 255, 0))

def draw_board(screen):
    """
    Vykreslí kompletní herní scénu: pozadí, jamky, pokladnice, 
    semena, jména hráčů a aktuální skóre.

    Args:
        screen (pygame.Surface): Plocha pro vykreslení.
    """
    width, height = screen.get_size()
    # PODMÍNKA: Zkontroluje, zda se podařilo načíst obrázek pozadí (background_texture).
    if background_texture:
        # Pokud textura existuje, nejdříve ji pomocí 'transform.scale' roztáhne na celou velikost okna.
        # Poté ji pomocí 'blit' vykreslí na pozici (0, 0) – tedy do levého horního rohu.
        screen.blit(pygame.transform.scale(background_texture, (width, height)), (0, 0))
    else:
        screen.fill((180, 140, 100))

    # 1. Najde vodorovný střed okna (např. u šířky 1280 je to 640)
    center_screen_x = width // 2
    # 2. Dynamicky vypočítá velikost jamky:
    #Vezme dostupnou šířku (šířka - 400), vydělí ji počtem jamek a 
    #pomocí min/max zajistí, aby jamka nebyla menší než 50 a větší než 90 pixelů.
    pit_size = min(90, max(50, (width - 400) // PITS_PER_SIDE))
    # 3. Určí vzdálenost mezi středy sousedních jamek (velikost jamky + mezera 30px)
    spacing = pit_size + 30
    # 4. Vypočítá svislou pozici pro Hráče 2 (horní řada): 
    #Střed obrazovky mínus výška jamky mínus rezerva 20px směrem nahoru
    p2_y = height // 2 - pit_size - 20
    # 5. Vypočítá svislou pozici pro Hráče 1 (dolní řada):
    #Střed obrazovky plus rezerva 20px směrem dolů
    p1_y = height // 2 + 20
    # 6. Vypočítá počáteční X-ovou souřadnici (zleva), aby celá řada jamek 
    #byla perfektně vycentrovaná vzhledem ke středu obrazovky
    start_x = center_screen_x - (PITS_PER_SIDE - 1) * spacing / 2

    # Vykreslení počitadla tahů v rohu
    moves_text = font.render(f"Tahů: {MOVE_COUNT}", True, (200, 200, 200))
    # Umístíme například do pravého horního rohu s malým okrajem
    screen.blit(moves_text, (width - moves_text.get_width() - 20, 20))

    # Vykreslení důlků pro hráče
    for i in range(PITS_PER_SIDE):
        pit_x = int(start_x + i * spacing)
        # dolní řada = hráč 1
        index_p1 = i
        # horní řada = hráč 2 (reverzní orientace)
        index_p2 = 2 * PITS_PER_SIDE - i

        # 1. Prochází dvojice: (svislá pozice, index v poli board) pro obě řady jamek v jednom sloupci
        for y_offset, index in [(p1_y, index_p1), (p2_y, index_p2)]:
            # 2. Kontrola, zda se podařilo načíst obrázek (texturu) pro jamku
            if hole_texture:
                # 3. Změní velikost textury na aktuální pit_size a vykreslí ji na souřadnice [pit_x, y_offset]
                screen.blit(pygame.transform.scale(hole_texture, (pit_size, pit_size)), (pit_x, y_offset))
            else:
                # 4. Pokud textura chybí, vykreslí jamku jako hnědou elipsu (náhradní řešení)
                pygame.draw.ellipse(screen, (100, 70, 40), (pit_x, y_offset, pit_size, pit_size))
            # 5. Zavolá funkci pro vykreslení kuliček (semen) rozptýlených kolem středu jamky
            draw_seeds(screen, board[index], pit_x + pit_size // 2, y_offset + pit_size // 2, radius=int(pit_size * 0.3))
            # 6. Vytvoří (vyrenderuje) textový objekt s číslem, které odpovídá počtu semen v dané jamce
            num = font.render(str(board[index]), True, (255, 255, 255))
            # 7. Vykreslí toto číslo přesně na střed jamky (výpočet: střed jamky mínus polovina šířky/výšky textu)
            screen.blit(num, (pit_x + pit_size // 2 - num.get_width() // 2, y_offset + pit_size // 2 - num.get_height() // 2))

    # Vykreslení pokladnic (Mancaly)
    mancala_width = pit_size
    mancala_height = pit_size * 2 + 20
    p1_mancala_x = int(start_x + PITS_PER_SIDE * spacing)
    p2_mancala_x = int(start_x - spacing)
    mancala_y = height // 2 - mancala_height // 2

    for pit_x, index in [(p1_mancala_x, index_p1_mancala()), (p2_mancala_x, index_p2_mancala())]:
        pygame.draw.rect(screen, (80, 50, 30), (pit_x, mancala_y, mancala_width, mancala_height), border_radius=20)
        pygame.draw.rect(screen, (40, 25, 15), (pit_x, mancala_y, mancala_width, mancala_height), 3, border_radius=20)
        draw_seeds(screen, board[index], pit_x + mancala_width // 2, mancala_y + mancala_height // 2, radius=int(mancala_width * 0.25))

   # --- DYNAMICKÉ ZABARVENÍ PODLE SKÓRE ---
    s1 = board[index_p1_mancala()]
    s2 = board[index_p2_mancala()]

    # Výchozí bílá barva
    color1 = (255, 255, 255)
    color2 = (255, 255, 255)

    # Pokud někdo vede, změníme mu barvu na červenou (nebo třeba zlatou (255, 215, 0))
    if s1 > s2:
        color1 = (255, 50, 50)  # Hráč 1 vede
    elif s2 > s1:
        color2 = (255, 50, 50)  # Hráč 2 vede

    p1_label = font.render(f"{player1_name}: {s1}", True, color1)
    p2_label = font.render(f"{player2_name}: {s2}", True, color2)
    
    screen.blit(p1_label, (p1_mancala_x, mancala_y + mancala_height + 10))
    screen.blit(p2_label, (p2_mancala_x, mancala_y + mancala_height + 10))

    # Stavové texty
    if not game_over:
        status = player1_name if current_player == 0 else player2_name
        color = (50, 100, 255) if current_player == 0 else (255, 80, 80)
        status_text = font.render(f"Na tahu: {status}", True, color)
        screen.blit(status_text, (center_screen_x - status_text.get_width() // 2, 40))
    else:
        if board[index_p1_mancala()] > board[index_p2_mancala()]: res = f"{player1_name} vyhrál!"
        elif board[index_p2_mancala()] > board[index_p1_mancala()]: res = f"{player2_name} vyhrál!"
        else: res = "Remíza!"
        status_text = MENU_FONT.render(res, True, (255, 215, 0))
        screen.blit(status_text, (center_screen_x - status_text.get_width() // 2, 30))
        guide = font.render("ESC pro menu", True, (200, 200, 200))
        screen.blit(guide, (center_screen_x - guide.get_width() // 2, height - 50))
    
    # --- Zobrazení potvrzení resetu ---
    if r_clicks == 1:
        # Vytvoříme žlutý text
        confirmation_text = font.render("Opravdu restartovat? Stiskni znovu R", True, (255, 255, 0))
        
        # Vycentrujeme ho nad spodní okraj
        text_x = width // 2 - confirmation_text.get_width() // 2
        text_y = height - 100  # O kousek výš než "ESC pro menu", aby se nepřekrývaly
        
        # Vykreslíme
        screen.blit(confirmation_text, (text_x, text_y))
    
    screen.blit(font.render("Zmáčkněte U pro undo", True, (255, 255, 0)), (20, 0 + undo_offset_y))
    

# ==============================
#  ČÁST 4 — HLAVNÍ SMYČKA A MENU
# ==============================

def draw_text_center(screen, text, y, color=(240, 240, 240)):
    """
    Vykreslí textový řetězec vycentrovaný horizontálně na obrazovce.

    Args:
        screen (pygame.Surface): Plocha pro vykreslení.
        text (str): Text k zobrazení.
        y (int): Vertikální pozice textu.
        color (tuple, optional): Barva textu v RGB. Výchozí je světle šedá.
    """
    status_text = MENU_FONT.render(text, True, color)
    screen.blit(status_text, (screen.get_width() // 2 - status_text.get_width() // 2, y))

def index_from_click(pos, screen):
    """
    Přepočítá souřadnice kliknutí myši na index konkrétní jamky.

    Args:
        pos (tuple): Souřadnice kliknutí (pit_x, y).
        screen (pygame.Surface): Plocha použitá pro dynamický výpočet rozložení.

    Returns:
        int: Index jamky v poli board, nebo None, pokud bylo kliknuto mimo jamky.
    """
    # 1. Zjistí aktuální rozměry okna
    width, height = screen.get_size()
    # 2. Uloží střed obrazovky a souřadnice myši z parametru 'pos' do samostatných proměnných
    center_screen_x, mouse_x, mouse_y = width // 2, pos[0], pos[1]
    # 3. Zopakuje stejný výpočet velikosti jamky jako ve 'draw_board', aby detekce seděla na grafiku
    pit_size = min(90, max(50, (width - 400) // PITS_PER_SIDE))
    # 4. Definice rozestupů a vertikálních pozic obou řad (musí být shodné s vykreslováním)
    spacing = pit_size + 30
    p2_y = height // 2 - pit_size - 20
    p1_y = height // 2 + 20
    # 5. Vypočítá levý okraj první jamky, aby mohl začít testovat kolize zleva doprava
    start_x = center_screen_x - (PITS_PER_SIDE - 1) * spacing / 2
    # 6. Prochází všechny sloupce jamek jednu po druhé
    for i in range(PITS_PER_SIDE):
        # 7. Vypočítá vodorovnou pozici X pro aktuální sloupec (i)
        pit_x = int(start_x + i * spacing)
        # 8. TEST PRO SPODNÍ ŘADU: Je kurzor v rozmezí Y (výška) a zároveň v rozmezí X (šířka) jamky?
        if p1_y <= mouse_y <= p1_y + pit_size and pit_x <= mouse_x <= pit_x + pit_size:
            # Vrátí index (0 až 6), což odpovídá jamkám prvního hráče
            return i
        # 9. TEST PRO HORNÍ ŘADU: Stejný test, ale pro svislou souřadnici 'p2_y'
        if p2_y <= mouse_y <= p2_y + pit_size and pit_x <= mouse_x <= pit_x + pit_size:
            # Vrátí index v opačném pořadí (pro PITS_PER_SIDE=7 to vrací indexy 14 až 8)
            return 2 * PITS_PER_SIDE - i
    return None

state = "MENU"
windowed_mode = user_settings["windowed_mode"]
apply_mode = True
screen = None
clock = pygame.time.Clock()

# Hlavní smyčka aplikace
while True:
    # Kontrola příznaku 'apply_mode'. Pokud je True, hráč v nastavení změnil režim zobrazení.
    if apply_mode:
        if windowed_mode: screen = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
        else: screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        
        # Uložení nové volby do slovníku a následný zápis do souboru (aby si hra volbu pamatovala).
        user_settings["windowed_mode"] = windowed_mode
        save_settings(user_settings)
        apply_mode = False
    
    mouse_x, mouse_y = pygame.mouse.get_pos()
    # Prochází frontu událostí (klávesy, myš, systémové zprávy), které se nahromadily od minule.
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()

            # --- DEBUG OVLÁDÁNÍ (Šipky) ---
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                undo_offset_y -= 5  # Posune text výš
            if event.key == pygame.K_DOWN:
                undo_offset_y += 5  # Posune text níž
            if event.key == pygame.K_p:
                print(f"Aktuální Y offset pro Undo: {undo_offset_y}")
        
        # --- Ovládání vstupu jmen ---
        if state == "NAME_INPUT" and event.type == pygame.KEYDOWN:
            # --- KLÁVESA ENTER: Potvrzení zadání ---
            if event.key == pygame.K_RETURN:
                # Pokud píše 1. hráč a jméno není prázdné (.strip() odstraní mezery), přepne na 2. hráče.
                if active_input == 1 and player1_name.strip(): active_input = 2
                # Pokud píše 2. hráč a jméno je v pořádku, přepne hru do stavu "GAME" a resetuje desku.
                elif active_input == 2 and player2_name.strip(): 
                    state = "GAME"
                    reset_game()
            elif event.key == pygame.K_BACKSPACE:
                # Pomocí "slicingu" [:-1] odstraní poslední znak z řetězce aktuálního hráče.
                if active_input == 1: player1_name = player1_name[:-1]
                else: player2_name = player2_name[:-1]
            elif event.key == pygame.K_ESCAPE: state = "MENU"
            else:
                # LIMIT DÉLKY: Zkontroluje, zda jméno nepřesáhlo 12 znaků (aby se vešlo do UI).
                if len(player1_name if active_input == 1 else player2_name) < 12:
                    # FILTR: Povolí pouze alfanumerické znaky (písmena, čísla) nebo mezeru.
                    if event.unicode.isalnum() or event.unicode == " ":
                        # Přidá stisknutý znak (event.unicode) k aktuálnímu jménu.
                        if active_input == 1: player1_name += event.unicode
                        else: player2_name += event.unicode

        if event.type == pygame.KEYDOWN:
            if state == "SETTINGS":
                if event.key == pygame.K_RETURN: # RETURN = Enter
                    windowed_mode = not windowed_mode
                    apply_mode = True
                if event.key == pygame.K_ESCAPE: state = "MENU"
            elif state == "GAME": 
                if event.key == pygame.K_ESCAPE: state = "MENU"
                if event.key == pygame.K_u:
                        if previous_board is not None: # Jen pokud už proběhl aspoň jeden tah
                            board = previous_board.copy() # Obnoví stav herního pole
                            current_player = previous_player # Vrátí tah správnému hráči
                            # Po použití Undo fotku smažeme, aby nešlo skákat do nekonečna 
                            previous_board = None
                            MOVE_COUNT -= 1 # Snížíme počet tahů o 1, protože se vracíme zpět
                if event.key == pygame.K_r:
                        r_clicks += 1
                        if r_clicks == 2:
                            reset_game()
                            r_clicks = 0

        if event.type == pygame.MOUSEBUTTONDOWN:
            if state == "MENU":
                # Pomocná proměnná pro svislý střed obrazovky (pro výpočet tlačítek)
                height_middle = screen.get_height() // 2
                # DETEKCE TLAČÍTEK:
                # Tlačítko HRÁT: Kontroluje, zda je myš v rozmezí Y pro první položku
                if height_middle - 80 < mouse_y < height_middle - 20: 
                    # Resetuje jména a přepne na obrazovku zadávání jmen
                    player1_name = ""; player2_name = ""; active_input = 1
                    state = "NAME_INPUT"
                # Tlačítko NASTAVENÍ: Rozmezí Y pro druhou položku
                elif height_middle < mouse_y < height_middle + 50: state = "SETTINGS"
                # Tlačítko KONEC: Rozmezí Y pro poslední položku
                elif height_middle + 60 < mouse_y < height_middle + 140: pygame.quit(); sys.exit()
            elif state == "GAME" and not game_over:
                # PŘEVOD SOUŘADNIC: Funkce index_from_click zjistí, na kterou jamku (index) hráč klikl
                index = index_from_click((mouse_x, mouse_y), screen)
                if index is not None:
                    # POJISTKA: Tah se provede jen pokud:
                    # Je na tahu hráč 1 (0) a klikl na svou jamku (is_p1_pit)
                    # NEBO je na tahu hráč 2 (1) a klikl na svou jamku (is_p2_pit)
                    if (current_player == 0 and is_p1_pit(index)) or (current_player == 1 and is_p2_pit(index)):
                        # Pokud je vše v pořádku, spustí se samotná logika rozesévání kuliček
                        make_move(index)

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

    # AKTUALIZACE DISPLEJE: Vykreslí nakreslený snímek z paměti na monitor 
    pygame.display.flip()
    clock.tick(60)