#
# project imports
import commands as cmds
import soupbot_utilities as util


#
# Command Handler
class CommandHandler(object):
    # init
    def __init__(self, db_handler):
        self.db_handler = db_handler

    # handles commands sent by users
    def pass_command(self, command, author):
        #
        # local vars
        cmdArgs = command.content.split(" ")
        cmd = cmdArgs.pop(0)[1:]
        #
        # basic commands
        if cmd in cmds.BASIC_COMMANDS.keys():
            util.soup_log("[cmd] {s:8} command successful".format(s=cmd))
            return cmds.BASIC_COMMANDS[cmd](cmdArgs)
        #
        # db access commands
        if cmd in cmds.DB_ACCESS_COMMANDS.keys():
            util.soup_log("[cmd] {s:8} command successful".format(s=cmd))
            return cmds.DB_ACCESS_COMMANDS[cmd](self.db_handler, cmdArgs, author)
        #
        # defaults if an invalid command is passed
        else:
            return "none!@E"
