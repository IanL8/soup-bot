#
# functions
def read_data():
    temp = dict()
    f = open("src/bot_data.txt", "r")
    k = f.readline().rstrip()
    while len(k) > 0:
        c = f.readline()
        temp[k] = int(c)
        k = f.readline().rstrip()
    f.close()
    return temp


def write_data(d):
    f = open("src/bot_data.txt", "w")
    s = ""
    for k, v in d.items():
        s += k + "\n" + str(v) + "\n"
    f.write(s)
    f.close()


def get_fortunes():
    temp = []
    f = open("src/fort.txt")
    s = f.readline()
    while len(s) > 0:
        temp.insert(0, s)
        s = f.readline()
    f.close()
    return temp
