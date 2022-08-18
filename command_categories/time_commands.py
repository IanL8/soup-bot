#
# imports
import time
import asyncio

#
# project imports
from command_categories import commandHandler
import soupbot_utilities as util

#
# stopwatch
stopwatches = dict()
class Stopwatch:
    def __init__(self, uid, startTime):
        self.uid = uid
        self.startTime = startTime


# start stopwatch
@commandHandler.command("watch", "start a stopwatch with a given name", "time")
async def start_stopwatch(context):
    if len(context.args) == 0:
        return await context.channel.send("no name specified")

    name = util.list_to_string(context.args, " ")
    if name in stopwatches.keys():
        return await context.channel.send(f"the name *{name}* is already in use")

    stopwatches[name] = Stopwatch(context.author.id, time.time())
    await context.message.add_reaction("✅")


# check stopwatch
@commandHandler.command("check", "check a stopwatch", "time")
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
@commandHandler.command("stop", "stop a stopwatch", "time")
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


# get stopwatches created by a user
@commandHandler.command("get_watches", "get all stopwatches made by the author", "time")
async def get_stopwatches(context):
    msg = "```\n"
    flag = False
    for k, v in stopwatches.items():
        if v.uid == context.author.id:
            msg += f"{k}\n"
            flag = True
    msg += "```"

    if not flag:
        return await context.channel.send("no stopwatches created by user")

    await context.channel.send(msg)

#
# timer

async def timer_helper(uid, channel, endTime: int):
    while True:
        await asyncio.sleep(.9)
        if int(time.time()) == endTime:
            return await channel.send(f"<@{uid}>")

# start timer
@commandHandler.command("timer", "start a timer with a given duration [no commas]", "time")
async def timer(context):
    if len(context.args) == 0:
        return await context.channel.send("no end time specified")

    # parse end time
    i = 0
    sec = 0
    args = context.args
    while i < len(args):
        if args[i].isdigit():
            num = int(args[i])
            mult = 1
            if i+1 < len(args):
                i += 1                          # increment pos var
                if args[i].startswith("s"):
                    mult = 1
                elif args[i].startswith("m"):
                    mult = 60
                elif args[i].startswith("h"):
                    mult = 3600
                elif args[i].startswith("d"):
                    mult = 86400
                else:
                    i -= 1                      # decrement pos var
            sec += num * mult
        else:
            return await context.channel.send("invalid time")
        i += 1                                  # increment pos var

    endTime = int(time.time() + sec)
    asyncio.run_coroutine_threadsafe(timer_helper(context.author.id, context.channel, endTime), context.bot.loop)
    await context.message.add_reaction("✅")
