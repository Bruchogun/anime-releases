from discord.ext import commands
import discord
import sqlite3
import requests

PREFIX = "!"
TOKEN = "MTA1ODUzMzQxMzkxODg4Mzg2MA.GNWixj.egNStMATJ84wQl1E_T9bRSF-hpq2yCCZIVeKTw"

class LinkButton(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

def run():
    db_conexion = sqlite3.connect("anime_db")
    cursor = db_conexion.cursor()
    intent = discord.Intents.all()
    bot = commands.Bot(command_prefix = PREFIX, intents = intent, description = "Bot anime scraper")

    @bot.command(name = "recent", help="Give you the last N episodes released (20 Max)")
    async def recent(ctx, n = 1):
        n = int(n)
        if n > 20 or n < 1:
            n = 1
        cursor.execute("SELECT * FROM recent_episodes")
        recent_episodes = cursor.fetchall()
        for i in reversed(range(n)):
            response = requests.get(recent_episodes[i][2])
            open("temporary/recent_episode.jpeg", "wb").write(response.content)
            view = LinkButton()
            view.add_item(discord.ui.Button(label= "Download episode", style=discord.ButtonStyle.link, url = recent_episodes[i][3]))
            view.add_item(discord.ui.Button(label= "Go to page", style=discord.ButtonStyle.link, url = recent_episodes[i][3]))
            await ctx.send(f'{recent_episodes[i][0]}\nEpisode {recent_episodes[i][1]}', file = discord.File('temporary/recent_episode.jpeg'), view = view)

    bot.run(TOKEN)
    db_conexion.close()

if __name__ == '__main__':
    run()