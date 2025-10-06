CREATE TABLE players (
    player_id INT AUTO_INCREMENT PRIMARY KEY,
    nick VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100),
    password VARCHAR(255) NOT NULL,
    role ENUM('user','admin') DEFAULT 'user',
    joined_on DATE DEFAULT CURDATE()
);
