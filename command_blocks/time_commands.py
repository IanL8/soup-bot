#
# imports
import time
import asyncio

#
# project imports
from command_management.commands import Commands, CommandBlock
import soupbot_utilities as util

#
# stopwatch
class Stopwatch:
    def __init__(self, uid, startTime):
        self.uid = uid
        self.startTime = startTime


class TimeCommands(CommandBlock):

    name = "time commands"
    commands = Commands()

    def __init__(self):
        super().__init__()
        self.stopwatches = dict()

    @commands.command("stopwatch", "start a stopwatch with a given name", enable_input=True)
    async def start_stopwatch(self, context):
        if len(context.args) == 0:
            return await context.send_message("no name specified")

        name = util.list_to_string(context.args, " ")
        if name in self.stopwatches.keys():
            return await context.send_message(f"the name *{name}* is already in use")

        self.stopwatches[name] = Stopwatch(context.author.id, time.time())
        await context.confirm()

    @commands.command("check", "check a stopwatch", enable_input=True)
    async def check_stopwatch(self, context):
        if len(context.args) == 0:
            return await context.send_message("no stopwatch specified")

        name = util.list_to_string(context.args, " ")
        if name not in self.stopwatches.keys():
            msg = f"no stopwatch named *{name}*"
        else:
            msg = util.time_to_string(time.time() - self.stopwatches[name].startTime)

        await context.send_message(msg)

    @commands.command("stop", "stop a stopwatch", enable_input=True)
    async def stop_stopwatch(self, context):
        if len(context.args) == 0:
            return await context.send_message("no stopwatch specified")

        name = util.list_to_string(context.args, " ")
        if name not in self.stopwatches.keys():
            msg = f"no stopwatch named *{name}*"
        elif self.stopwatches[name].uid != context.author.id:
            msg = "this is not your stopwatch"
        else:
            current = time.time() - self.stopwatches[name].startTime
            self.stopwatches.pop(name)
            msg = f"*{name}* stopped at {util.time_to_string(current)}"

        await context.send_message(msg)

    @commands.command("get_watches", "get all stopwatches made by you")
    async def get_stopwatches(self, context):
        msg = "```\n"
        flag = False
        for k, v in self.stopwatches.items():
            if v.uid == context.author.id:
                msg += f"{k}\n"
                flag = True
        msg += "```"

        if not flag:
            return await context.send_message("no stopwatches created by user")

        await context.send_message(msg)

    @staticmethod
    async def timer_helper(uid, channel, end_time):
        while True:
            await asyncio.sleep(.9)
            if int(time.time()) == end_time:
                return await channel.send(f"<@{uid}>")

    @commands.command("timer", "start a timer with a given duration [no commas]", enable_input=True)
    async def timer(self, context):
        if len(context.args) == 0:
            return await context.send_message("no end time specified")

        # parse end time
        i = 0
        sec = 0
        args = context.args
        while i < len(args):
            if args[i].isdigit():
                num = int(args[i])
                multi = 1
                if i+1 < len(args):
                    i += 1                          # increment pos var
                    if args[i].startswith("s"):
                        multi = 1
                    elif args[i].startswith("m"):
                        multi = 60
                    elif args[i].startswith("h"):
                        multi = 3600
                    elif args[i].startswith("d"):
                        multi = 86400
                    else:
                        i -= 1                      # decrement pos var
                sec += num * multi
            else:
                return await context.send_message("invalid time")
            i += 1                                  # increment pos var

        end_time = int(time.time() + sec)
        asyncio.run_coroutine_threadsafe(self.timer_helper(context.author.id, context.channel, end_time), context.bot.loop)
        await context.confirm()
