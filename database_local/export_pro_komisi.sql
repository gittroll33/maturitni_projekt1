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
INSERT INTO "ucast_v_zapasu" VALUES(2,3,25,1);
INSERT INTO "ucast_v_zapasu" VALUES(3,3,23,0);
INSERT INTO "ucast_v_zapasu" VALUES(2,4,25,1);
INSERT INTO "ucast_v_zapasu" VALUES(3,4,23,0);
CREATE TABLE uzivatele (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    jmeno TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    heslo TEXT NOT NULL,
    role TEXT DEFAULT 'user'
);
INSERT INTO "uzivatele" VALUES(1,'Admin','admin@spskladno.cz','admin123','admin');
INSERT INTO "uzivatele" VALUES(2,'Hráč 2','hrac2@game.local','password','user');
INSERT INTO "uzivatele" VALUES(3,'Hráč 3','hrac3@game.local','password','user');
INSERT INTO "uzivatele" VALUES(4,'Lucka','lucka@volny.cz','heslo3','user');
CREATE TABLE zapasy (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    datum TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
INSERT INTO "zapasy" VALUES(1,'2026-02-08 16:15:47');
INSERT INTO "zapasy" VALUES(2,'2026-02-08 16:39:32');
INSERT INTO "zapasy" VALUES(3,'2026-02-08 16:41:00');
INSERT INTO "zapasy" VALUES(4,'2026-02-08 16:47:57');
DELETE FROM "sqlite_sequence";
INSERT INTO "sqlite_sequence" VALUES('uzivatele',4);
INSERT INTO "sqlite_sequence" VALUES('zapasy',4);
COMMIT;
