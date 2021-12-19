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

    #
    # on connection to discord
    async def on_ready(self):
        print(self.user.name + " has connected to Discord")
        for g in self.guilds:
            self.commandHandlers[g] = command_handler.CommandHandler(self.user.name, str(g), FLAG)

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


client = SoupBotClient()
client.run(TOKEN)
