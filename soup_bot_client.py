#
# imports
import os
import discord
from dotenv import load_dotenv

#
# project imports
import commands
import database_handler as db
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
        # init tables
        db.init()
        #
        # init cmd_handler
        self.cmdHandler = commands.get_cmd_handler()

    # on connection to discord
    async def on_ready(self):
        for g in self.guilds:
            if not db.add_guild(g):
                util.soup_log("[ERROR] {s} could not be added to the db".format(s=g.name))
        util.soup_log(self.user.name + " has connected to Discord")

    # on close
    async def close(self):
        util.soup_log(self.user.name + " has disconnected from Discord")

    # on guild join
    async def on_guild_join(self, guild):
        if not db.add_guild(guild):
            util.soup_log("[ERROR] {s} could not be added to the db".format(s=guild.name))

    # on member join
    async def on_member_join(self, member):
        if not db.add_member(member.id, member.guild.id):
            util.soup_log("[ERROR] {s}:{k} could not be added to the db".format(s=member.name, k=member.id))

    # on message
    async def on_message(self, message):
        if message.author == self.user:
            return

        flag = message.content[0]
        cmdArgs = message.content.split(" ")
        cmd = cmdArgs.pop(0)[1:]

        if db.get_flag(message.guild) == flag and self.cmdHandler.is_cmd(cmd):
            temp = self.cmdHandler.pass_cmd(cmd, message, cmdArgs)
            await message.channel.send(temp)
