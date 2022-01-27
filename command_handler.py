#
# imports
import random
import urllib.request

#
# project imports
import soupbot_utilities as util


class CommandHandler(object):
    #
    # init
    def __init__(self, name, guild, flag):
        self.name = name
        self.guild = guild
        self.flag = flag

    #
    # handles basic commands
    def pass_command(self, command, name):
        cmdList = command.split(" ")
        #
        # help
        if command.startswith(self.flag + "help"):
            return "Commands: hello, bye, roll <d#>(100 default), word, phrase <number of words>, 8ball <question>, " \
                   "lookup <league name>, which <options separated by commas>, fortune, git"
        #
        # hello
        elif command.startswith(self.flag + "hello"):
            return "hello " + name
        #
        # bye
        elif command.startswith(self.flag + "bye"):
            return "bye " + name
        #
        # roll
        elif command.startswith(self.flag + "roll"):
            if len(cmdList) == 1 or not cmdList[1].isdigit() or cmdList[1] == "0":
                temp = int(random.random() * 100) + 1
            else:
                temp = int(random.random() * int(cmdList[1])) + 1
            return str(temp)
        #
        # word
        elif command.startswith(self.flag + "word"):
            return util.WORD_LIST[int(random.random() * len(util.WORD_LIST))]
        #
        # phrase
        elif command.startswith(self.flag + "phrase"):
            temp = ""
            k = 2
            if len(cmdList) > 1 and cmdList[1].isdigit() and cmdList[1] != "0":
                k = int(cmdList[1])
            for i in range(k):
                temp = temp + util.WORD_LIST[int(random.random() * len(util.WORD_LIST))] + " "
            return temp
        #
        # 8ball
        elif command.startswith(self.flag + "8ball"):
            return util.MAGIC_8BALL_LIST[int(random.random() * len(util.MAGIC_8BALL_LIST))]
        #
        # lookup
        elif command.startswith(self.flag + "lookup"):
            if len(cmdList) == 1:
                return "No name specified."
            return "https://na.op.gg/summoner/userName=" + cmdList[1]
        #
        # which
        elif command.startswith(self.flag + "which"):
            if len(cmdList) == 1:
                return "No options specified."
            temp = command.replace(self.flag + "which", "").split(",")
            return temp[int(random.random() * len(temp))].lstrip()
        #
        # git
        elif command.startswith(self.flag + "git"):
            return "https://github.com/IanL8/soup-bot"
        #
        # true
        elif command.startswith(self.flag + "true"):
            return ("TRUE" if random.random() > .49 else "FALSE") + " <:LULW:801145828923408453>"
        #
        # defaults if an invalid command is passed
        elif command.startswith(self.flag + "fortune"):
            return util.FORTUNES[int(random.random() * len(util.FORTUNES))]
        #
        # defaults if an invalid command is passed
        else:
            return "none!@E"
