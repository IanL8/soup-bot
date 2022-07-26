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
        return await context.channel.send(f"the name *{name}* is already in use")

    stopwatches[name] = Stopwatch(context.author.id, time.time())
    await context.message.add_reaction("✅")



# check stopwatch
@commandHandler.command("check", "check a stopwatch")
async def check_stopwatch(context):
    if len(context.args) == 0:
        return await context.channel.send("no stopwatch specified")

    name = util.list_to_string(context.args, " ")
    if name not in stopwatches.keys():
        msg = f"no stopwatch named *{name}*"
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
        msg = f"no stopwatch named *{name}*"
    elif stopwatches[name].uid != context.author.id:
        msg = "this is not your stopwatch"
    else:
        current = time.time() - stopwatches[name].startTime
        stopwatches.pop(name)
        msg = f"*{name}* stopped at {util.time_to_string(current)}"

    await context.channel.send(msg)
