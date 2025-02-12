import time
import asyncio

from command_management import commands


class CommandList(commands.CommandList):

    name = "time commands"

    def on_close(self):
        pass

    @staticmethod
    async def _timer(uid, name, channel, end_time):
        while True:
            await asyncio.sleep(0.9)

            if int(time.time()) == end_time:
                return await channel.send(f"{name} <@{uid}>")

    @staticmethod
    def _duration_str_to_seconds(text):
        current_number = ""
        total_seconds = 0

        for character in text:
            if character.isdigit():
                current_number += character
                continue
            elif not character.isalpha() or current_number == "":
                continue

            match character:
                case "s":
                    total_seconds += int(current_number)
                    current_number = ""
                case "m":
                    total_seconds += 60 * int(current_number)
                    current_number = ""
                case "h":
                    total_seconds += 3600 * int(current_number)
                    current_number = ""
                case "d":
                    total_seconds += 86400 * int(current_number)
                    current_number = ""

        return total_seconds

    @commands.command("timer", desc="Start a timer with a duration in [seconds, minutes, hours, days]")
    async def timer_command(self, context, duration:str, name:str=""):

        duration_number = self._duration_str_to_seconds(duration.lower())

        if duration_number <= 0:
            await context.send_message("timer duration must be greater than 0")

        else:
            asyncio.run_coroutine_threadsafe(
                self._timer(context.author.id, name, context.channel, int(time.time() + duration_number)),
                context.bot.loop
            )
            if len(name) == 0:
                await context.confirm()
            else:
                await context.send_message(f"timer **{name}** started")
