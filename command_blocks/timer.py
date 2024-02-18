import time
import asyncio
from functools import reduce

from command_management import Commands, CommandBlock


class Block(CommandBlock):

    name = "time commands"
    commands = Commands()

    @staticmethod
    async def timer_helper(uid, channel, end_time):
        while True:
            await asyncio.sleep(0.9)
            if int(time.time()) == end_time:
                return await channel.send(f"<@{uid}>")

    @commands.command("timer", "start a timer with the given duration [seconds, minutes, hours, days accepted]", enable_input=True)
    async def timer(self, context):
        if len(context.args) == 0:
            return await context.send_message("no timer duration given")

        str_args = reduce(lambda x, y: f"{x}{y}", context.args).lower()

        c_num = ""
        duration = 0

        for i in range(len(str_args)):
            if str_args[i].isdigit():
                c_num += str_args[i]
            elif str_args[i].isalpha():
                if c_num == "":
                    continue
                elif str_args[i] == "s":
                    duration += int(c_num)
                    c_num = ""
                elif str_args[i] == "m":
                    duration += 60 * int(c_num)
                    c_num = ""
                elif str_args[i] == "h":
                    duration += 3600 * int(c_num)
                    c_num = ""
                elif str_args[i] == "d":
                    duration += 86400 * int(c_num)
                    c_num = ""

        if duration == 0:
            return await context.send_message("timer duration must be greater than 0")

        asyncio.run_coroutine_threadsafe(
            self.timer_helper(context.author.id, context.channel, int(time.time() + duration)),
            context.bot.loop
        )
        await context.confirm()
