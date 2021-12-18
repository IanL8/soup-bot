#
# imports
import random
import urllib.request

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


class BotCommand:
    def __init__(self, name, flag):
        self.name = name
        self.flag = flag
        temp = str(urllib.request.urlopen(word_site).read()).replace("b'", "")
        self.words = temp.split("\\n")

    def pass_command(self, command, name):
        cmdList = command.split(" ")
        #
        # help
        if command.startswith(self.flag + "help"):
            return "Commands: hello, bye, roll <d#>(100 default), word, phrase <number of words>, 8ball <question>, " \
                   "lookup <league name>, which <options separated by commas>, git"
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
            return self.words[int(random.random() * len(self.words))]
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
        else:
            return "none!@E"
