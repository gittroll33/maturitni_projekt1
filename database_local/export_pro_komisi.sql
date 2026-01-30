BEGIN TRANSACTION;
CREATE TABLE ucast_v_zapasu (
    uzivatel_id INTEGER,
    zapas_id INTEGER,
    skore INTEGER,
    je_vitez BOOLEAN,
    PRIMARY KEY (uzivatel_id, zapas_id),
    FOREIGN KEY (uzivatel_id) REFERENCES uzivatele(id) ON DELETE CASCADE,
    FOREIGN KEY (zapas_id) REFERENCES zapasy(id) ON DELETE CASCADE
);
INSERT INTO "ucast_v_zapasu" VALUES(2,1,25,1);
INSERT INTO "ucast_v_zapasu" VALUES(3,1,15,0);
CREATE TABLE ucult_v_zapasu (
    uzivatel_id INTEGER,
    zapas_id INTEGER,
    skore INTEGER,
    je_vitez BOOLEAN,
    PRIMARY KEY (uzivatel_id, zapas_id),
    FOREIGN KEY (uzivatel_id) REFERENCES uzivatele(id) ON DELETE CASCADE,
    FOREIGN KEY (zapas_id) REFERENCES zapasy(id) ON DELETE CASCADE
);
CREATE TABLE uzivatele (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    jmeno TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    heslo TEXT NOT NULL,
    role TEXT DEFAULT 'user'
);
INSERT INTO "uzivatele" VALUES(1,'Petr','petr@seznam.cz','hash1','user');
INSERT INTO "uzivatele" VALUES(2,'Honza','honza@gmail.com','hash2','user');
INSERT INTO "uzivatele" VALUES(3,'Lucka','lucka@volny.cz','hash3','user');
CREATE TABLE zapasy (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    datum TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
INSERT INTO "zapasy" VALUES(1,'2026-01-30 13:51:03');
DELETE FROM "sqlite_sequence";
INSERT INTO "sqlite_sequence" VALUES('uzivatele',9);
INSERT INTO "sqlite_sequence" VALUES('zapasy',1);
COMMIT;
