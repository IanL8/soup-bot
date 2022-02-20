#
# imports
import urllib.request
import time


#
# functions
def read_file_to_list(src):
    temp = []
    f = open(src)
    s = f.readline()
    while len(s) > 0:
        temp.insert(0, s)
        s = f.readline().strip()
    f.close()
    return temp


def time_to_string(t):
    timeUnits = [(86400, "days"), (3600, "hours"), (60, "min")]
    s = ""
    for i, j in timeUnits:
        temp = int(t / i)
        t = t % i
        if temp > 0:
            s += str(temp) + " " + j + ", "
    if t > 0:
        s += str(int(t)) + " sec"
    else:
        s = s[:len(s)-2]
    return s


def get_date():
    t = time.localtime()
    return "{month:02}/{day:02}: {hour:02}:{minute:02}:{sec:02}"\
        .format(month=t[1], day=t[2], hour=t[3], minute=t[4], sec=t[5])


def timed_message(s):
    print("{date}: {msg}".format(date=get_date(), msg=s))


#
# constants
MAGIC_8BALL_LIST = ["It is certain.",
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
# WORD_LIST = str(urllib.request.urlopen("https://www.mit.edu/~ecprice/wordlist.10000").read()).replace("b'", "") \
#     .split("\\n")
WORD_LIST = read_file_to_list("src/word_list.txt")
FORTUNES = read_file_to_list("src/fort.txt")
