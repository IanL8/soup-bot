#
# imports
import time

#
# project imports
from command_handler import commandHandler
import soupbot_utilities as util

#
# stopwatch
stopwatches = dict()
class Stopwatch:
    def __init__(self, uid, startTime):
        self.uid = uid
        self.startTime = startTime


# start stopwatch
@commandHandler.command("start", "start a stopwatch with a given name")
async def start_stopwatch(context):
    if len(context.args) == 0:
        return await context.channel.send("no name specified")

    name = util.list_to_string(context.args, " ")
    if name in stopwatches.keys():
        msg = "the name *{}* is already in use".format(name)
    else:
        stopwatches[name] = Stopwatch(context.author.id, time.time())
        msg = "stopwatch *{}* started".format(name)

    await context.channel.send(msg)


# check stopwatch
@commandHandler.command("check", "check a stopwatch")
async def check_stopwatch(context):
    if len(context.args) == 0:
        return await context.channel.send("no stopwatch specified")

    name = util.list_to_string(context.args, " ")
    if name not in stopwatches.keys():
        msg = "no stopwatch named *{}*".format(name)
    else:
        msg = util.time_to_string(time.time() - stopwatches[name].startTime)

    await context.channel.send(msg)


# stop stopwatch
@commandHandler.command("stop", "stop a stopwatch")
async def stop_stopwatch(context):
    if len(context.args) == 0:
        return await context.channel.send("no stopwatch specified")

    name = util.list_to_string(context.args, " ")
    if name not in stopwatches.keys():
        msg = "no stopwatch named *{}*".format(name)
    elif stopwatches[name].uid != context.author.id:
        msg = "this is not your stopwatch"
    else:
        current = time.time() - stopwatches[name].startTime
        stopwatches.pop(name)
        msg = "*{}* stopped at {}".format(name, util.time_to_string(current))

    await context.channel.send(msg)


# get stopwatches
@commandHandler.command("stopwatches", "list all active stopwatches")
async def get_stopwatches(context):
    if len(stopwatches) == 0:
        msg = "no stopwatches"
    else:
        msg = util.list_to_string(stopwatches.keys(), ", ")

    await context.channel.send(msg)