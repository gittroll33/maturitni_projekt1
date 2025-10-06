-- Žebříček hráčů pro konkrétní hru
SELECT u.username, g.name AS game_name, s.level, s.score, s.last_play
FROM scores s
JOIN users u ON s.user_id = u.id
JOIN games g ON s.game_id = g.id
WHERE g.name = 'SkoreHra'
ORDER BY s.score DESC
LIMIT 10;

-- Top hráči ve všech hrách
SELECT u.username, g.name AS game_name, SUM(s.score) AS total_score
FROM scores s
JOIN users u ON s.user_id = u.id
JOIN games g ON s.game_id = g.id
GROUP BY u.username, g.name
ORDER BY total_score DESC;

-- Zobrazení členů týmů (M:N)
SELECT t.name AS team_name, u.username
FROM team_members tm
JOIN teams t ON tm.team_id = t.id
JOIN users u ON tm.user_id = u.id
ORDER BY t.name, u.username;

-- Hráči s více než 1 skóre v konkrétní hře
SELECT u.username, COUNT(*) AS games_played
FROM scores s
JOIN users u ON s.user_id = u.id
WHERE s.game_id = 1
GROUP BY u.username
HAVING games_played > 1;
