#
# imports
import random
import time

#
# project imports
import soupbot_utilities as util
import database_handler


def find_user_id(user_id, li):
    for element in li:
        for e in element:
            if user_id == e:
                return True
    return False


class CommandHandler(object):
    #
    # init
    def __init__(self, name, guild, flag):
        self.name = name
        self.guild = guild
        self.flag = flag

    #
    # handles basic commands
    def pass_command(self, command, author):
        cmdList = command.split(" ")
        #
        # help
        if command.startswith(self.flag + "help"):
            return "Commands: hello, bye, roll <d#>(100 default), word, phrase <number of words>, 8ball <question>, " \
                   "lookup <league name>, which <options separated by commas>, fortune, git"
        #
        # hello
        elif command.startswith(self.flag + "hello"):
            return "hello " + author.name
        #
        # bye
        elif command.startswith(self.flag + "bye"):
            return "bye " + author.name
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
        # fortune
        elif command.startswith(self.flag + "fortune"):
            k, li = database_handler.make_query("SELECT user_id FROM UserTimers")
            if k == 0:
                return "[Error] Bad query"
            userId = str(author.id)
            i = 0
            if not find_user_id(userId, li):
                k, li = database_handler.make_query("INSERT INTO UserTimers (timer_name, user_id) VALUES (%s, %s);",
                                                    ("fortune", userId))
                if k == 0:
                    return "[Error] Bad query"
            else:
                k, temp = database_handler.make_query("SELECT start_time FROM UserTimers WHERE user_id=%s;", (userId,))
                if k == 0:
                    return "[Error] Bad query"
                i = temp[0][0]
            t = time.time() - i
            if t < 72000:
                return util.time_to_string(72000 - t) + " until next fortune redeem."

            k, li = database_handler.make_query("UPDATE UserTimers SET start_time=%s WHERE user_id=%s;",
                                                (int(time.time()), userId))
            if k == 0:
                return "[Error] Bad query"

            return util.FORTUNES[int(random.random() * len(util.FORTUNES))]
        #
        # defaults if an invalid command is passed
        else:
            return "none!@E"
