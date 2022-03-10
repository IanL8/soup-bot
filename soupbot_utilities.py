#
# imports
import time


#
# functions

# find k in cursor.execute() output
def find_in_list(k, li):
    for elements in li:
        for e in elements:
            if k == e:
                return True
    return False


# creates a list of strings from a txt file
def read_file_to_list(src):
    temp = []
    f = open(src)
    s = f.readline()
    while len(s) > 0:
        temp.insert(0, s)
        s = f.readline().strip()
    f.close()
    return temp


# creates a string from a list with sep between the elements
def list_to_string(li, sep=" "):
    temp = ""
    for i, e in enumerate(li):
        if i < len(li)-1:
            temp += e.strip() + sep
        else:
            temp += e
    return temp


# takes a time t in seconds and gives the time in days, hours, min, sec
def time_remaining_to_string(t):
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


# returns the current date and time
def get_date():
    t = time.localtime()
    return "{month:02}/{day:02}: {hour:02}:{minute:02}:{sec:02}"\
        .format(month=t[1], day=t[2], hour=t[3], minute=t[4], sec=t[5])


# prints a message s with a timestamp
def soup_log(s):
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
WORD_LIST = read_file_to_list("src/word_list.txt")  # list of words from https://www.mit.edu/~ecprice/wordlist.10000
FORTUNES = read_file_to_list("src/fort.txt")
