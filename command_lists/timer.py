import time
import asyncio

from command_management import commands


class CommandList(commands.CommandList):

    name = "time commands"

    def on_close(self):
        pass

    @staticmethod
    async def _timer(uid, channel, end_time):
        while True:
            await asyncio.sleep(0.9)

            if int(time.time()) == end_time:
                return await channel.send(f"<@{uid}>")

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

    @commands.command("timer", desc="start a timer with a duration in [seconds, minutes, hours, days]", enable_input=True)
    async def timer_command(self, context):
        if len(context.content) == 0:
            await context.send_message("no timer duration given")
            return

        duration = self._duration_str_to_seconds(context.content.lower())

        if duration <= 0:
            await context.send_message("timer duration must be greater than 0")

        else:
            asyncio.run_coroutine_threadsafe(
                self._timer(context.author.id, context.channel, int(time.time() + duration)),
                context.bot.loop
            )
            await context.confirm()
