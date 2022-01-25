#
# imports
import os
import discord
from dotenv import load_dotenv

#
# project imports
import command_handler

#
# get .env values
load_dotenv("values.env")
TOKEN = os.getenv("DISCORD_TOKEN")
FLAG = os.getenv("BOT_FLAG")


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
        print(self.user.name + " has connected to Discord")
        for g in self.guilds:
            self.commandHandlers[g] = command_handler.CommandHandler(self.user.name, str(g), FLAG)

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
            temp = handler.pass_command(message.content, str(message.author.name))
            if temp == "none!@E":
                pass
            else:
                await message.channel.send(temp)

    #
    # on close
    async def close(self):
        command_handler.close()
        print(self.user.name + " has disconnected from Discord")


client = SoupBotClient()
client.run(TOKEN)
