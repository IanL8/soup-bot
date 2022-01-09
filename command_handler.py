#
# imports
import random
import urllib.request

#
# project imports
import file_handler as fh

#
# global vars
word_site = "https://www.mit.edu/~ecprice/wordlist.10000"

magic_8_ball_options = ["It is certain.",
                        "It is decidedly so.",
                        "Without a doubt.",
                        "Yes – definitely.",
                        "You may rely on it.",
                        "As I see it, yes.",
                        "Most likely.",
                        "Outlook good.",
                        "Yes.",
                        "Signs point to yes.",
                        "Reply hazy, try again.",
                        "Ask again later.",
                        "Better not tell you now.",
                        "Cannot predict now.",
                        "Concentrate and ask again.",
                        "Don't count on it.",
                        "My reply is no.",
                        "My sources say no.",
                        "Outlook not so good.",
                        "Very doubtful."
                        ]


data = fh.get_data()


#
# functions
def get_words():
    temp = str(urllib.request.urlopen(word_site).read()).replace("b'", "")
    return temp.split("\\n")


def finalize():
    fh.write_data(data)


class CommandHandler(object):
    #
    # constants
    WORDS = get_words()

    #
    # init
    def __init__(self, name, guild, flag):
        self.name = name
        self.guild = guild
        self.flag = flag
        self.counter = 0
        if guild in data.keys():
            self.counter = data[guild]
        else:
            data[guild] = 0

    #
    # handles basic commands
    def pass_command(self, command, name):
        cmdList = command.split(" ")
        #
        # help
        if command.startswith(self.flag + "help"):
            return "Commands: hello, bye, roll <d#>(100 default), word, phrase <number of words>, 8ball <question>, " \
                   "lookup <league name>, which <options separated by commas>, count, git"
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
            temp = None
            if len(cmdList) == 1 or not cmdList[1].isdigit() or cmdList[1] == "0":
                temp = int(random.random() * 100) + 1
            else:
                temp = int(random.random() * int(cmdList[1])) + 1
            return str(temp)
        #
        # word
        elif command.startswith(self.flag + "word"):
            return self.WORDS[int(random.random() * len(self.WORDS))]
        #
        # phrase
        elif command.startswith(self.flag + "phrase"):
            temp = ""
            k = 2
            if len(cmdList) > 1 and cmdList[1].isdigit() and cmdList[1] != "0":
                k = int(cmdList[1])
            for i in range(k):
                temp = temp + self.words[int(random.random() * len(self.words))] + " "
            return temp
        #
        # 8ball
        elif command.startswith(self.flag + "8ball"):
            return magic_8_ball_options[int(random.random() * len(magic_8_ball_options))]
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
        # counter
        elif command.startswith(self.flag + "counter"):
            return "Current value: " + str(self.counter)
        #
        # count
        elif command.startswith(self.flag + "count"):
            s = ""
            if random.random() < .01:
                self.counter = 0
                s = "Oh no! " + name + " has reset the counter to "
            else:
                self.counter += 1
            data[self.guild] = self.counter
            return s + str(self.counter)
        #
        # true
        elif command.startswith(self.flag + "true"):
            return ("TRUE" if random.random() > .49 else "FALSE") + " <:LULW:801145828923408453>"
        #
        # defaults if an invalid command is passed
        else:
            return "none!@E"
