#
# functions
def get_data():
    temp = dict()
    f = open("bot_data.txt", "r")
    k = f.readline().rstrip()
    while len(k) > 0:
        c = f.readline()
        temp[k] = int(c)
        k = f.readline().rstrip()
    f.close()
    return temp


def write_data(d):
    f = open("bot_data.txt", "w")
    s = ""
    for k, v in d.items():
        s += k + "\n" + str(v) + "\n"
    f.write(s)
    f.close()
