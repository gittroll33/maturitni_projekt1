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
CREATE TABLE IF NOT EXISTS ucult_v_zapasu (
    uzivatel_id INTEGER,
    zapas_id INTEGER,
    skore INTEGER,
    je_vitez BOOLEAN,
    PRIMARY KEY (uzivatel_id, zapas_id),
    FOREIGN KEY (uzivatel_id) REFERENCES uzivatele(id) ON DELETE CASCADE,
    FOREIGN KEY (zapas_id) REFERENCES zapasy(id) ON DELETE CASCADE
);

-- Vzorová data pro maturitu (3 záznamy)
INSERT OR IGNORE INTO uzivatele (jmeno, email, heslo) VALUES 
('Petr', 'petr@seznam.cz', 'hash1'),
('Honza', 'honza@gmail.com', 'hash2'),
('Lucka', 'lucka@volny.cz', 'hash3');