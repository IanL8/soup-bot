#
# project imports
import commands as cmds


#
# an instance of CommandHandler is made for each guild
class CommandHandler(object):
    # init
    def __init__(self, name, guild, flag):
        self.name = name
        self.guild = guild
        self.flag = flag

    # handles commands sent by users
    def pass_command(self, command, author):
        #
        # local vars
        cmdArgs = command.split(" ")
        cmd = cmdArgs.pop(0)[1:]
        #
        # basic commands
        if cmd in cmds.COMMAND_LIST.keys():
            return cmds.COMMAND_LIST[cmd](cmdArgs, author)
        #
        # defaults if an invalid command is passed
        else:
            return "none!@E"
