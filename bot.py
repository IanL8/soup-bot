#
# imports
import os
import discord
from dotenv import load_dotenv
#
# project imports
import bot_command
#
# get .env values
load_dotenv("values.env")
TOKEN = os.getenv("DISCORD_TOKEN")
FLAG = os.getenv("BOT_FLAG")

#
# global vars
botCMD = bot_command.BotCommand("SoupBot", FLAG)


class SoupBotClient(discord.Client):
    #
    # init
    async def on_ready(self):
        print(f'{self.user} has connected to Discord')

    #
    # on message
    async def on_message(self, message):
        if message.author == self.user:
            return

        if message.content.startswith(FLAG):
            temp = botCMD.pass_command(message.content, str(message.author.name))
            if temp == "none!@E":
                pass
            else:
                await message.channel.send(temp)


client = SoupBotClient()
client.run(TOKEN)
