PRAGMA foreign_keys = ON;

-- Tabulka uživatelů (BCNF normalizace)
CREATE TABLE IF NOT EXISTS uzivatele (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    jmeno TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    heslo TEXT NOT NULL,
    role TEXT DEFAULT 'user'
);

-- Tabulka zápasů
CREATE TABLE IF NOT EXISTS zapasy (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    datum TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Vazební tabulka pro vztah M:N (Hráči vs Zápasy)
CREATE TABLE IF NOT EXISTS ucast_v_zapasu (
    uzivatel_id INTEGER,
    zapas_id INTEGER,
    skore INTEGER,
    je_vitez BOOLEAN,
    PRIMARY KEY (uzivatel_id, zapas_id),
    FOREIGN KEY (uzivatel_id) REFERENCES uzivatele(id) ON DELETE CASCADE,
    FOREIGN KEY (zapas_id) REFERENCES zapasy(id) ON DELETE CASCADE
);

--- VZOROVÁ DATA PRO MATURITU ---

-- 1. Uživatelé (včetně admina pro test mazání)
INSERT OR IGNORE INTO uzivatele (id, jmeno, email, heslo, role) VALUES 
(1, 'Admin', 'admin@spskladno.cz', 'admin123', 'admin'),
(2, 'Petr', 'petr@seznam.cz', 'heslo1', 'user'),
(3, 'Honza', 'honza@gmail.com', 'heslo2', 'user'),
(4, 'Lucka', 'lucka@volny.cz', 'heslo3', 'user');

-- 2. Vzorový zápas (aby JOIN v žebříčku něco našel)
INSERT OR IGNORE INTO zapasy (id, datum) VALUES (1, CURRENT_TIMESTAMP);

-- 3. Výsledky (Petr vs Honza)
-- Petr (ID 2) vyhrál 25:15
INSERT OR IGNORE INTO ucast_v_zapasu (uzivatel_id, zapas_id, skore, je_vitez) VALUES 
(2, 1, 25, 1),
(3, 1, 15, 0);