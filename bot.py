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
MYSQL_USERNAME, MYSQL_PASSWORD = os.getenv("MYSQL_USERNAME"), os.getenv("MYSQL_PASSWORD")
MYSQL_HOST, MYSQL_DB = os.getenv("MYSQL_HOST"), os.getenv("MYSQL_DB")


#
# soupbot
class SoupBotClient(discord.Client):
    # init
    def __init__(self, **options):
        super().__init__(**options)
        #
        # init and connect to db
        self.dbHandler = database_handler.DatabaseHandler(MYSQL_USERNAME, MYSQL_PASSWORD, MYSQL_HOST, MYSQL_DB)
        self.dbHandler.connect()
        #
        # init cmd_handler
        self.cmdHandlers = dict()

    # on connection to discord
    async def on_ready(self):
        for g in self.guilds:
            if self.dbHandler.add_guild(g) == 0:
                util.soup_log("[ERROR] {s} could not be added to the db".format(s=g.name))
            self.cmdHandlers[g] = command_handler.CommandHandler(self.dbHandler, str(g.id))
        util.soup_log(self.user.name + " has connected to Discord")

    # on close
    async def close(self):
        self.dbHandler.disconnect()
        util.soup_log(self.user.name + " has disconnected from Discord")

    # on guild join
    async def on_guild_join(self, guild):
        self.cmdHandlers[guild] = command_handler.CommandHandler(self.dbHandler)
        if self.dbHandler.add_guild(guild) == 0:
            util.soup_log("[ERROR] {s} could not be added to the db".format(s=guild.name))

    # on message
    async def on_message(self, message):
        if message.author == self.user:
            return
        if message.content.startswith(self.cmdHandlers[message.guild].get_flag()):
            temp = self.cmdHandlers[message.guild].pass_command(message, message.author)
            if temp == "none!@E":
                pass
            else:
                if type(temp) == discord.Embed:
                    await message.channel.send(embed=temp)
                    return
                await message.channel.send(temp)


#
# start bot
intents = discord.Intents.all()
client = SoupBotClient(intents=intents)
client.run(TOKEN)
