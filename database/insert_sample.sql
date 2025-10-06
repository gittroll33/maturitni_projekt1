-- Vložení testovacích uživatelů
INSERT INTO users (username, password, role) VALUES
('tomas', 'tajne1', 'user'),
('anna', 'tajne2', 'user'),
('admin', 'adminpass', 'admin');

-- Vložení testovacích her
INSERT INTO games (name, description) VALUES
('SkoreHra', 'Jednoduchá hra pro testování'),
('RychlaHra', 'Hra s časovým limitem'),
('Strategie', 'Strategická hra');

-- Vložení testovacích skóre
INSERT INTO scores (user_id, game_id, level, score, last_play) VALUES
(1, 1, 1, 150, '2025-10-06'),
(1, 2, 2, 200, '2025-10-06'),
(2, 1, 1, 120, '2025-10-06');

-- Vložení testovacích týmů
INSERT INTO teams (name) VALUES ('Tým Alfa'), ('Tým Beta'), ('Tým Gamma');

-- Vložení členů týmů (M:N)
INSERT INTO team_members (team_id, user_id) VALUES
(1,1), (1,2), (2,2), (2,3), (3,1), (3,3);
