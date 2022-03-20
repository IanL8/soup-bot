#
# project imports
import commands as cmds
import soupbot_utilities as util


#
# Command Handler
class CommandHandler(object):
    # init
    def __init__(self, dbHandler, guildID):
        self.dbHandler = dbHandler
        self.guildID = guildID
        self.flag = dbHandler.get_flag(guildID)

    def get_flag(self):
        return self.flag

    def set_flag(self, f):
        self.flag = f

    # handles commands sent by users
    def pass_command(self, command, author):
        #
        # local vars
        cmdArgs = command.content.split(" ")
        cmd = cmdArgs.pop(0)[1:]
        #
        # basic commands
        if cmd in cmds.BASIC_COMMANDS.keys():
            return cmds.BASIC_COMMANDS[cmd](cmdArgs)
        #
        # db access commands
        if cmd in cmds.DB_ACCESS_COMMANDS.keys():
            return cmds.DB_ACCESS_COMMANDS[cmd](cmdArgs, self.dbHandler, str(author.id), str(self.guildID))
        #
        # admin access commands
        if cmd in cmds.ADMIN_COMMANDS.keys():
            return cmds.ADMIN_COMMANDS[cmd](cmdArgs, self.dbHandler, self, str(author.id), self.guildID)
        #
        # defaults if an invalid command is passed
        else:
            return "none!@E"
