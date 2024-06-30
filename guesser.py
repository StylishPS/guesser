import discord
from discord.ext import commands
import names as n
import random as r
import asyncio as asc
from datetime import datetime
import sqlite3 as sql

# Токен, префикс, разрешения
TOKEN = 'MTE5NTYxMzA2OTEyOTI5Nzk5MA.G0fec1.t7IGTikGHXzSYeeGo5WpHz01AqGLzsC3VwaUnI'
PREFIX = '%'
intents = discord.Intents().all()
bot = commands.Bot(
    command_prefix=PREFIX, 
    intents=intents
)
bot.remove_command('help')

connection = sql.connect('server.db')
cursor = connection.cursor()

# Переменные
iterations = 0

# Создание таблицы базы данных
@bot.event
async def on_ready():
    cursor.execute("""CREATE TABLE IF NOT EXISTS users (
        users_id INT AUTO_INCREMENT PRIMARY KEY,
        name TEXT,
        discord_id INT,
        points INT,
        guessed_total INT
        guessed_easy INT,
        guessed_medium INT,
        guessed_hard INT
    )""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS levels (
        levels_id INT AUTO_INCREMENT PRIMARY KEY,
        level_name TEXT               
    )""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS users_levels (
        users_levels_id INT AUTO_INCREMENT PRIMARY KEY,
        users_id INT NOT NULL,
        levels_id INT,
        FOREIGN KEY (users_id) REFERENCES users (users_id),
        FOREIGN KEY (levels_id) REFERENCES levels (levels_id)
    )""")
    connection.commit()

    for guild in bot.guilds:
        for member in guild.members:
            if cursor.execute(f"SELECT id FROM users WHERE id = {member.id}").fetchone() is None:
                cursor.execute(f"INSERT INTO users VALUES ('{member}', {member.id}, 0, 0, 0, 0, 0)")
                connection.commit()
@bot.event
async def on_member_join(member):
    if cursor.execute(f"SELECT id FROM users WHERE id = {member.id}").fetchone() is None:
        cursor.execute(f"INSERT INTO users VALUES ('{member}', {member.id}, 0, 0, 0, 0, 0)")
        connection.commit()

# Команда угадывания
@bot.command(aliases=["guess", "угамага", "угагага", "угадать"])
async def угадалка(ctx, difficulty=None):
    global randint, guessed_answer, iterations
    iterations += 1
    if iterations > 1:
        await ctx.reply("В канале уже идет игра!")
        return # Окончание функции команды
    else:
        pass
    randint = r.randint(1, 3)
    if difficulty is None:
        diff = r.randint(0, 2)
        if diff == 0:
            easy()
        elif diff == 1:
            medium()
        elif diff == 2:
            hard()
    elif difficulty == "изи" or difficulty == "easy":
        easy()
    elif difficulty == "медиум" or difficulty == "medium":
        medium()
    elif difficulty == "хард" or difficulty == "hard":
        hard()
    else:
        diff = r.randint(0, 2) # Рандомная сложность
        if diff == 0:
            easy()
        elif diff == 1:
            medium()
        elif diff == 2:
            hard()
    await ctx.reply(embed = embed, mention_author = False) # Отправка эмбедов
    timeout = 14 # Первоначальный таймаут
    timestamp = datetime.now().timestamp() # Временная метка на момент написания команды
    while True:
        try:
            guessed_answer = await bot.wait_for('message', timeout = timeout) # Инпут ответа
        except asc.TimeoutError:
            await ctx.send("Время вышло!")
            iterations = 0 # Обнуление задач
            break
        new_timestamp = datetime.now().timestamp() # Текущая временная метка
        timeout = timestamp + 14 - new_timestamp # Если человек напишет неверное сообщение до обнуления таймера
        if guessed_answer.content.lower() == name: # Если человек угадал
            author = guessed_answer.author.mention # Упрощение упоминания пользователя
            await guessed_answer.add_reaction('✅') # Реакция на правильный ответ
            await ctx.send(f"{author} угадал(а) уровень.") # Отправка сообщения о победе
            cursor.execute("UPDATE users SET points = points + 1 WHERE id = {}".format(guessed_answer.author.id)) # Прибавление очков
            connection.commit() # Подтверждение изменений
            iterations = 0 # Обнуление задач
            if cursor.execute("SELECT"): # Если нету элемента в списке
                cursor.execute("UPDATE users SET guessed = guessed + 1 WHERE id = {}".format(guessed_answer.author.id)) # Обновление угаданных уровней
                connection.commit() # Подтверждение изменений
                if name in n.easy:
                    cursor.execute("UPDATE users SET guessed_easy = guessed_easy + 1 WHERE id = {}".format(guessed_answer.author.id)) # Обновление угаданных уровней
                elif name in n.medium:
                    cursor.execute("UPDATE users SET guessed_medium = guessed_medium + 1 WHERE id = {}".format(guessed_answer.author.id)) # Обновление угаданных уровней
                elif name in n.hard:
                    cursor.execute("UPDATE users SET guessed_hard = guessed_hard + 1 WHERE id = {}".format(guessed_answer.author.id)) # Обновление угаданных уровней
            break # Завершение цикла

# Статистика игрока
@bot.command(aliases=["stats", "статистика"])
async def стата(ctx, member: discord.Member = None):
    if member is None:
        embed = discord.Embed(
            title = "Ваша статистика:",
            description = f"☕ **Очки:** {cursor.execute("SELECT points FROM users WHERE id = {}".format(ctx.author.id)).fetchone()[0]}\n\n 🎀 **Угаданные уровни**: {cursor.execute("SELECT guessed FROM users WHERE id = {}".format(ctx.author.id)).fetchone()[0]} / {n.names}\n 🟢 **Угаданные легкие уровни**: {cursor.execute("SELECT guessed_easy FROM users WHERE id = {}".format(ctx.author.id)).fetchone()[0]} / {list(n.easy)[-1]}\n 🟡 **Угаданные средние уровни**: {cursor.execute("SELECT guessed_normal FROM users WHERE id = {}".format(ctx.author.id)).fetchone()[0]} / {list(n.medium)[-1]}\n 🔴 **Угаданные сложные уровни**: {cursor.execute("SELECT guessed_hard FROM users WHERE id = {}".format(ctx.author.id)).fetchone()[0]} / {list(n.hard)[-1]}",
            colour = discord.Colour.from_rgb(158, 160, 255)
        )
        await ctx.reply(embed = embed, mention_author = False)
    else:
        embed = discord.Embed(
            title = f"Статистика игрока {member.nick}:",
            description = f"☕ **Очки:** {cursor.execute("SELECT points FROM users WHERE id = {}".format(member.id)).fetchone()[0]}\n\n 🎀 **Угаданные уровни**: {cursor.execute("SELECT guessed FROM users WHERE id = {}".format(member.id)).fetchone()[0]} / {n.names}\n 🟢 **Угаданные легкие уровни**: {cursor.execute("SELECT guessed_easy FROM users WHERE id = {}".format(member.id)).fetchone()[0]} / {list(n.easy)[-1]}\n 🟡 **Угаданные средние уровни**: {cursor.execute("SELECT guessed_normal FROM users WHERE id = {}".format(member.id)).fetchone()[0]} / {list(n.medium)[-1]}\n 🔴 **Угаданные сложные уровни**: {cursor.execute("SELECT guessed_hard FROM users WHERE id = {}".format(member.id)).fetchone()[0]} / {list(n.hard)[-1]}",
            colour = discord.Colour.from_rgb(158, 160, 255)
        )
        await ctx.reply(embed = embed, mention_author = False)

# Инфо по боту
@bot.command()
async def хелп(ctx):
    await ctx.send("Мои команды: **%угадалка [сложность]**")

# Эмбеды
def easy():
    global embed, name
    embed = discord.Embed(
        title = "Угадалка",
        description = "**Сложность**: Лёгкая",
        colour = discord.Colour.from_rgb(110, 227, 75)
    )
    name = f"{n.easy[f"{randint}"]}"
    embed.set_image(url=f"https://github.com/StylishPS/guesser_thumbnails/blob/main/easy/{randint}.png?raw=true") 
def medium():
    global embed, name
    embed = discord.Embed(
        title = "Угадалка",
        description = "**Сложность**: Средняя",
        colour = discord.Colour.from_rgb(243, 214, 52)
    )
    name = f"{n.medium[f"{randint}"]}"
    embed.set_image(url=f"https://github.com/StylishPS/guesser_thumbnails/blob/main/medium/{randint}.png?raw=true") 
def hard():
    global embed, name
    embed = discord.Embed(
        title = "Угадалка",
        description = "**Сложность**: Хард",
        colour = discord.Colour.from_rgb(235, 64, 52)
    )
    name = f"{n.hard[f"{randint}"]}"
    embed.set_image(url=f"https://github.com/StylishPS/guesser_thumbnails/blob/main/hard/{randint}.png?raw=true")
bot.run(TOKEN)