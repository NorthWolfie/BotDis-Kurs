import os
import random
import sqlite3

import discord
from discord import client
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)
Sessions = []
begin = False


class Player:
    def __init__(self, id, dices, diceres):
        self.id = id
        self.dices = dices
        self.diseres = diceres


def modify(a):
    global begin
    begin = a


@bot.event
async def on_ready():

    print('Бот запустился')

    global base, cur, server, ListRoles
    ListRoles = {}
    base = sqlite3.connect('BotDB.db')
    cur = base.cursor()
    server = 733774997306343495
    for role in bot.get_guild(server).roles:
        ListRoles[role.name] = role.id
    if base:
        print('DataBase connected...OK')


@bot.command()
@commands.has_role("Завадила")
async def playperudo(ctx):
    if begin is False:
        modify(True)
        author = ctx.author.name
        ID = ctx.author.id
        result = cur.execute('SELECT Peso FROM PERUDO WHERE Name = ? OR Id = ?', (author, ID)).fetchone()
        if result is None:
            cur.execute('INSERT INTO PERUDO VALUES (?, ?, ?)', (ID, author, 100))
            base.commit()
        result = cur.execute('SELECT Peso FROM PERUDO WHERE Name = ? OR Id = ?', (author, ID)).fetchone()
        man = Player(ID, 5, [])
        party = [man]
        Sessions.append(party)
        await ctx.send(f'{ctx.author.mention}, у вас {str(result[0])} песо')
    else:
        await ctx.send("Вы не можете начать новую игру пока не закончится набор для предыдущей!")


@bot.command()
@commands.has_role("Завадила")
async def begingame(ctx):
    modify(False)
    await ctx.send('Игра началась! Бросайте кости')
    count = 0
    for m in Sessions:
        if Sessions[user.author][0] == m[0]:
            count = count + 1
    if count >= 3 or count <= 6:
        modify(False)
        await ctx.send('Игра началась! Бросайте кости')
    elif count > 6:
        await ctx.send('Есть лишние люди')
    elif count < 3:
        await ctx.send('Не хватает людей для игры')



@bot.command()
@commands.has_role("Игрок")
async def join(ctx):
    if begin is True:
        author = ctx.author.name
        ID = ctx.author.id
        result = cur.execute('SELECT Peso FROM PERUDO WHERE Name = ? OR Id = ?', (author, ID)).fetchone()
        if result is None:
            cur.execute('INSERT INTO PERUDO VALUES (?, ?, ?)', (ID, author, 100))
            base.commit()
        result = cur.execute('SELECT Peso FROM PERUDO WHERE Name = ? OR Id = ?', (author, ID)).fetchone()
        last = len(Sessions)
        man = Player(id, 5, [])
        Sessions[last].append(man)
        await ctx.send(f'{ctx.author.mention}, у вас {str(result[0])} песо')
    else:
        await ctx.send("Вы опоздали, дождитесь начала следующей сессии")


@bot.command()
@commands.has_role("Игрок")
async def rollDice(ctx):
    author = ctx.author.id
    num = 0
    for i in Sessions:
        for j in i:
            if j.id == author:
                num = j.dices
                res = []
                for r in range(num):
                    res.append(random.randint(1, 6))
                j.diceres = res
                await ctx.author.send(str(res))
                break
        if num != 0:
            break


@bot.command()
@commands.has_role("Игрок")
async def say(ctx, *args):  # !say 3 4
    author = ctx.author
    if str(args[0]).lower() == "верю":
        await ctx.send(f'{author.mention}, повышай номинал!')
    elif str(args[0]).lower() == "не верю":
        index = None
        summary = [0, 0, 0, 0, 0, 0]
        sessnum = None
        for i in Sessions:
            for j in i:
                if j.id == author.id:
                    index = i.index(j)
                    sessnum = Sessions.index(i)
                    break
            if sessnum is not None:
                break
        sess = Sessions[sessnum]
        outcome = ""
        for i in sess:
            nextpl = client.get_user(int(i.id))
            outcome = outcome + f"{nextpl.name}: {i.diceres}\n"
            for d in i.diceres:
                if int(d) == 1:
                    summary[2] = summary[2] + 1
                    summary[3] = summary[3] + 1
                    summary[4] = summary[4] + 1
                    summary[5] = summary[5] + 1
                    summary[6] = summary[6] + 1
                else:
                    summary[int(d)] = summary[int(d)] + 1
        outsum = f"{2} - {summary[2]}; {3} - {summary[3]}; {4} - {summary[4]};" \
                 f"{5} - {summary[5]}; {6} - {summary[6]}"
        await ctx.send(f"{outsum}\n\n{outsum}")
    else:
        if int(args[1]) == 1:
            await ctx.send("С единиц ходить нельзя!")
        else:
            index = 0
            for i in Sessions:
                for j in i:
                    if j.id == author.id:
                        index = i.index(j) + 1
                        break
                if index < len(i) and index != 0:
                    break
                elif index > len(i):
                    index = 0
                    break
            nextpl = client.get_user(int(index))
            await ctx.send(f'{nextpl.mention}, ты следующий!')


bot.run(os.getenv('TOKEN'))
