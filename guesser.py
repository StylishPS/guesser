import discord
from discord.ext import commands
from discord import app_commands
import names as n
import random as r
import asyncio as asc
from datetime import datetime
import sqlite3 as sql
import repository

# Токен, префикс, разрешения
TOKEN = ''
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
    for difficulty in n.levels:
        for level in difficulty:
            repository.insertLevels(level['name'])

@bot.event
async def on_message(ctx):
    await bot.process_commands(ctx)

@bot.hybrid_command(name = 'reload', description="Reload thy commands")
@commands.is_owner()
async def reload(ctx):
    await ctx.send("Reloading commands...", ephemeral = True)
    await bot.tree.sync()
    await ctx.send("Reloaded the commands successfully", ephemeral = True)

# Команда угадывания
@bot.hybrid_command(name = "guess", description = "Start the guessing game.")
@app_commands.describe(difficulty = "Difficulty of level.")
async def угадалка(ctx, difficulty = None):
    global randint, guessed_answer, iterations
    iterations += 1
    if iterations > 1:
        await ctx.reply("There is already a going game on this channel!")
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
            await ctx.send(f"{author} have guessed the level.") # Отправка сообщения о победе
            repository.updateUserStatistics(guessed_answer.author.id)
            iterations = 0 # Обнуление задач
            break # Завершение цикла

def addGuessedLevel(discordId, levelName):
    userId = repository.getUserByDiscordId(discordId)
    levelId = repository.getLevelByName(levelName)
    repository.addGuessedLevel(userId, levelId)

@bot.hybrid_command(name = "ping", description = "Check the bot's latency responding the commands.")
async def ping(ctx):
    await ctx.reply(f"Pong 🏓! The bot's latency is {bot.latency * 1000:.0f}ms.")
    
# Статистика игрока
@bot.command(aliases=["stats", "статистика"])
async def стата(ctx, *, member: discord.Member = None):
    if member is None:
        embed = discord.Embed(
            title = "Your stats:",
            description = descriptionString(ctx.author.id),
            colour = discord.Colour.from_rgb(158, 160, 255)
        )
        await ctx.reply(embed = embed, mention_author = False)
    else:
        embed = discord.Embed(
            title = f"Stats of {member.display_name}:",
            description = descriptionString(member.id),
            colour = discord.Colour.from_rgb(158, 160, 255)
        )
        await ctx.reply(embed = embed, mention_author = False)

def descriptionString(discordId):
    userStatistics = repository.getUserStatistics(discordId)
    return  f"☕ **Очки:** {userStatistics["points"]}\n\n " \
        f"🎀 **Угаданные уровни**: {userStatistics["guessed_total"]} / {n.names}\n " \
        f"🟢 **Угаданные легкие уровни**: {userStatistics["guessed_easy"]} / {len(n.levels[0])}\n " \
        f"🟡 **Угаданные средние уровни**: {userStatistics["guessed_medium"]} / {len(n.levels[1])}\n " \
        f"🔴 **Угаданные сложные уровни**: {userStatistics["guessed_hard"]} / {len(n.levels[2])}"

# Инфо по боту
@bot.command()
async def хелп(ctx):
    await ctx.send("Мои команды: **%угадалка [сложность]**")

# Эмбеды
def easy():
    global embed, name
    randint = r.randint(0, len(n.levels[0]) - 1)
    embed = discord.Embed(
        title = "Угадалка",
        description = "**Сложность**: Лёгкая",
        colour = discord.Colour.from_rgb(110, 227, 75)
    )
    name = ((n.levels[0])[randint])['name']
    image = ((n.levels[0])[randint])['image']
    embed.set_image(url=f"{image}") 
def medium():
    global embed, name
    randint = r.randint(0, len(n.levels[1]) - 1)
    embed = discord.Embed(
        title = "Угадалка",
        description = "**Сложность**: Средняя",
        colour = discord.Colour.from_rgb(243, 214, 52)
    )
    name = ((n.levels[1])[randint])['name']
    image = ((n.levels[1])[randint])['image']
    embed.set_image(url=f"{image}")  
def hard():
    global embed, name
    randint = r.randint(0, len(n.levels[2]) - 1)
    embed = discord.Embed(
        title = "Угадалка",
        description = "**Сложность**: Хард",
        colour = discord.Colour.from_rgb(235, 64, 52)
    )
    name = ((n.levels[2])[randint])['name']
    image = ((n.levels[2])[randint])['image']
    embed.set_image(url=f"{image}") 
bot.run(TOKEN)
