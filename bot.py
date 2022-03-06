#
# imports
import os
import discord
from dotenv import load_dotenv

#
# project imports
import command_handler
import database_handler
import soupbot_utilities as util

#
# get .env values
load_dotenv("values.env")
TOKEN = os.getenv("DISCORD_TOKEN")
FLAG = os.getenv("BOT_FLAG")
MYSQL_USERNAME, MYSQL_PASSWORD = os.getenv("MYSQL_USERNAME"), os.getenv("MYSQL_PASSWORD")
MYSQL_HOST, MYSQL_DB = os.getenv("MYSQL_HOST"), os.getenv("MYSQL_DB")


#
# soupbot
class SoupBotClient(discord.Client):
    # init
    def __init__(self, **options):
        super().__init__(**options)
        self.intents.guilds = True
        #
        # init and connect to db
        self.db_handler = database_handler.DatabaseHandler(MYSQL_USERNAME, MYSQL_PASSWORD, MYSQL_HOST, MYSQL_DB)
        self.db_handler.connect()
        #
        # init cmd_handler
        self.cmd_handler = command_handler.CommandHandler(self.db_handler)

    # on connection to discord
    async def on_ready(self):
        util.soup_log(self.user.name + " has connected to Discord")

    # on close
    async def close(self):
        self.db_handler.disconnect()
        util.soup_log(self.user.name + " has disconnected from Discord")

    # on message
    async def on_message(self, message):
        if message.author == self.user:
            return

        if message.content.startswith(FLAG):
            temp = self.cmd_handler.pass_command(message, message.author)
            if temp == "none!@E":
                pass
            else:
                await message.channel.send(temp)


#
# start bot
client = SoupBotClient()
client.run(TOKEN)
