import discord
from discord.ext import commands
import names as n
import random as r
import asyncio as asc
from datetime import datetime
import sqlite3 as sql
import repository

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
repository = repository.Repository()

# Переменные
iterations = 0

@bot.event
async def on_ready():
    for level in n.levels:
        repository.insertLevels(n.levels['name'])

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
    repository.addUser(ctx.author.id, ctx.author.nick)
    while True:
        try:
            guessed_answer = await bot.wait_for('message', timeout = timeout) # Инпут ответа
        except asc.TimeoutError:
            await ctx.send("Время вышло!")
            iterations = 0 # Обнуление задач
            break
        new_timestamp = datetime.now().timestamp() # Текущая временная метка
        timeout = timestamp + 15 - new_timestamp # Если человек напишет неверное сообщение до обнуления таймера
        if guessed_answer.content.lower() == name: # Если человек угадал
            addGuessedLevel(guessed_answer.author.id, name)
            repository.addUser(guessed_answer.author.id, guessed_answer.author.nick)
            author = guessed_answer.author.mention # Упрощение упоминания пользователя
            await guessed_answer.add_reaction('✅') # Реакция на правильный ответ
            await ctx.send(f"{author} угадал(а) уровень.") # Отправка сообщения о победе
            repository.updateUserStatistics(guessed_answer.author.id)
            iterations = 0 # Обнуление задач
            break # Завершение цикла

def addGuessedLevel(discordId, levelName):
    userId = repository.getUserByDiscordId(discordId)
    levelId = repository.getLevelByName(levelName)
    repository.addGuessedLevel(userId, levelId)

# Статистика игрока
@bot.command(aliases=["stats", "статистика"])
async def стата(ctx, *, member: discord.Member = None):
    if member is None:
        embed = discord.Embed(
            title = "Ваша статистика:",
            description = descriptionString(ctx.author.id),
            colour = discord.Colour.from_rgb(158, 160, 255)
        )
        await ctx.reply(embed = embed, mention_author = False)
    else:
        embed = discord.Embed(
            title = f"Статистика игрока {member.nick}:",
            description = descriptionString(member.id),
            colour = discord.Colour.from_rgb(158, 160, 255)
        )
        await ctx.reply(embed = embed, mention_author = False)

def descriptionString(discordId):
    userStatistics = repository.getUserStatistics(discordId)
    return  f"☕ **Очки:** {userStatistics["points"]}\n\n " \
        f"🎀 **Угаданные уровни**: {userStatistics["guessed_total"]} / {n.names}\n " \
        f"🟢 **Угаданные легкие уровни**: {userStatistics["guessed_easy"]} / {list(n.easy)[-1]}\n " \
        f"🟡 **Угаданные средние уровни**: {userStatistics["guessed_medium"]} / {list(n.medium)[-1]}\n " \
        f"🔴 **Угаданные сложные уровни**: {userStatistics["guessed_hard"]} / {list(n.hard)[-1]}"


# Инфо по боту
@bot.command()
async def хелп(ctx):
    await ctx.send("Мои команды: **%угадалка [сложность]**")

# Эмбеды
def easy():
    global embed, name
    randint = r.randint(1, len(n.levels[0]))
    embed = discord.Embed(
        title = "Угадалка",
        description = "**Сложность**: Лёгкая",
        colour = discord.Colour.from_rgb(110, 227, 75)
    )
    name = ((n.levels[0])[randint])['name']
    embed.set_image(url=f"{((n.levels[0])[randint])['image']}") 
def medium():
    global embed, name
    randint = r.randint(1, len(n.levels[1]))
    embed = discord.Embed(
        title = "Угадалка",
        description = "**Сложность**: Средняя",
        colour = discord.Colour.from_rgb(243, 214, 52)
    )
    name = ((n.levels[1])[randint])['name']
    embed.set_image(url=f"{((n.levels[1])[randint])['image']}")  
def hard():
    global embed, name
    randint = r.randint(1, len(n.levels[2]))
    embed = discord.Embed(
        title = "Угадалка",
        description = "**Сложность**: Хард",
        colour = discord.Colour.from_rgb(235, 64, 52)
    )
    name = ((n.levels[2])[randint])['name']
    embed.set_image(url=f"{((n.levels[2])[randint])['image']}") 
bot.run(TOKEN)