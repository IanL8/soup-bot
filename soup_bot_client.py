#
# imports
import discord

#
# project imports
import commands
import database_handler as db
import soupbot_utilities as util


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
        self.cmdHandler = commands.get_command_handler()

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
        args = message.content.split(" ")
        cmd = args.pop(0)[1:]

        if db.get_flag(message.guild.id) == flag and self.cmdHandler.is_command(cmd):
            temp = self.cmdHandler.pass_command(cmd, message, args)
            await message.channel.send(temp)
