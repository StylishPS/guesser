import sqlite3 as sql
import names as n

class Repository:
    def __init__(self):
        self.connection = sql.connect('server.db')
        self.cursor = self.connection.cursor()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS users (
            users_id INT AUTO_INCREMENT PRIMARY KEY,
            name TEXT,
            discord_id INT,
            points INT,
            guessed_total INT,
            guessed_easy INT,
            guessed_medium INT,
            guessed_hard INT
        )""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS levels (
            levels_id INT AUTO_INCREMENT PRIMARY KEY,
            level_name TEXT,
            level_difficulty TEXT
        )""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS users_levels (
            users_levels_id INT AUTO_INCREMENT PRIMARY KEY,
            users_id INT NOT NULL,
            levels_id INT NOT NULL,
            FOREIGN KEY (users_id) REFERENCES users (users_id),
            FOREIGN KEY (levels_id) REFERENCES levels (levels_id)
        )""")
        self.connection.commit() # Подтверждение изменений

    def updateUserStatistics(self, discordId):
        self.cursor.execute("UPDATE users SET points = points + 1 WHERE discord_id = {}".format(discordId)) # Прибавление очков
        self.connection.commit() # Подтверждение изменений
 
    def addGuessedLevel(self, userId, levelId, name):
        if self.cursor.execute("SELECT level_name FROM users_levels WHERE users_id = {} AND levels_id = {}".format(userId, levelId).fetchone()) is None:
            self.cursor.execute("UPDATE users SET guessed_total = guessed_total + 1 WHERE users_id = {}".format(userId)) # Обновление угаданных уровней
            for difficulty in n.levels:
                for level in difficulty:
                    if name['difficulty'] == 'easy':
                        self.cursor.execute("UPDATE users SET guessed_easy = guessed_easy + 1 WHERE users_id = {}".format(userId)) # Обновление угаданных уровней
                    elif level[difficulty] == 'medium':
                        self.cursor.execute("UPDATE users SET guessed_medium = guessed_medium + 1 WHERE users_id = {}".format(userId)) # Обновление угаданных уровней
                    elif level[difficulty] == 'hard':
                        self.cursor.execute("UPDATE users SET guessed_hard = guessed_hard + 1 WHERE users_id = {}".format(userId)) # Обновление угаданных уровней
            self.connection.commit() # Подтверждение изменений

    def getUserStatistics(self, discordId):
        sql = "SELECT points, guessed_total, guessed_easy, guessed_medium, guessed_hard FROM users WHERE discord_id = {}".format(discordId)

        record = self.cursor.execute(sql).fetchone()
        if record is None:
            return {"points": 0, 
                    "guessed_total": 0, 
                    "guessed_easy": 0, 
                    "guessed_medium": 0, 
                    "guessed_hard": 0}            

        return {"points": record[0], 
                "guessed_total": record[1], 
                "guessed_easy": record[2], 
                "guessed_medium": record[3], 
                "guessed_hard": record[4]}
    
    def getUserByDiscordId(self, discordId):
        self.cursor.execute(f"SELECT name FROM users WHERE discord_id = {discordId}")

    def getLevelByName(self, levelName):
        self.cursor.execute(f"SELECT levels_id FROM levels WHERE level_name = '{levelName}'")

    def addUser(self, discordId, name):
        # userExists = self.cursor.execute("SELECT * FROM users WHERE discord_id = {}".format(discordId))
        # if len(userExists) is None:
        self.cursor.execute(f"INSERT INTO users VALUES (NULL, '{name}', {discordId}, 0, 0, 0, 0, 0)")
        self.connection.commit()

    def insertLevels(self, level, difficulty):
        sql = f"INSERT INTO levels VALUES (NULL, '{level}', '{difficulty}')"
        self.cursor.execute(sql)
        self.connection.commit()