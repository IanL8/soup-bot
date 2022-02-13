#
# imports
import os
import discord
from dotenv import load_dotenv

#
# project imports
import command_handler
import database_handler

#
# get .env values
load_dotenv("values.env")
TOKEN = os.getenv("DISCORD_TOKEN")
FLAG = os.getenv("BOT_FLAG")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")


class SoupBotClient(discord.Client):
    #
    # init
    def __init__(self, **options):
        super().__init__(**options)
        self.commandHandlers = dict()
        self.intents.guilds = True

    #
    # on connection to discord
    async def on_ready(self):
        for g in self.guilds:
            self.commandHandlers[g] = command_handler.CommandHandler(self.user.name, str(g), FLAG)
        if not database_handler.isConnected():
            database_handler.connect(MYSQL_PASSWORD)
            print("Connected to mysql")
        print(self.user.name + " has connected to Discord")

#
    # on close
    async def close(self):
        if database_handler.isConnected():
            database_handler.disconnect()
            print("Disconnected from mysql")
        print(self.user.name + " has disconnected from Discord")

    #
    # on guild join
    async def on_guild_join(self, guild):
        self.commandHandlers[guild] = command_handler.CommandHandler(self.user.name, str(guild), FLAG)

    #
    # on message
    async def on_message(self, message):
        if message.author == self.user:
            return
        handler = self.commandHandlers[message.guild]

        if message.content.startswith(FLAG):
            temp = handler.pass_command(message.content, message.author)
            if temp == "none!@E":
                pass
            else:
                await message.channel.send(temp)


client = SoupBotClient()
client.run(TOKEN)
