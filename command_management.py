# references the discord.py method of creating commands
# slightly different, though maintains many of the same features
# done to gain practice making larger scale projects + making python decorators
from discord import app_commands, Interaction, Message, Client

import soupbot_utilities as util


class Context:

    def __init__(self, args, message:Message=None, interaction:Interaction=None, bot:Client=None):

        if interaction is None:
            self._interaction = None
            self._message = message
            self._deferred = False
            self.is_basic = True
            self.bot = bot
            self.args = args
            self.channel = message.channel
            self.author = message.author
            self.guild = message.guild
            self.mentions = message.mentions

        else:
            self._interaction = interaction
            self._message = None
            self._deferred = False
            self.is_basic = False
            self.bot = interaction.client
            self.args = args
            self.channel = interaction.channel
            self.author = interaction.user
            self.guild = interaction.guild
            self.mentions = []

            if "resolved" in interaction.data.keys():
                self.mentions = [self.guild.get_member(int(i)) for i in interaction.data["resolved"]["users"].keys()]

    async def defer_message(self):
        if not self.is_basic:
            await self._interaction.response.defer()
            self._deferred = True

    async def send_message(self, s):
        if self.is_basic:
            msg = await self.channel.send(s)
        else:
            if self._deferred:
                await self._interaction.followup.send(s)
            else:
                await self._interaction.response.send_message(s)
            msg = await self._interaction.original_response()

        return msg

    async def confirm(self):
        if self.is_basic:
            await self._message.add_reaction("✅")
        else:
            if self._deferred:
                await self._interaction.followup.send("✅")
            else:
                await self._interaction.response.send_message("✅")

class Commands:

    def __init__(self):
        self.basic = dict() # cmd name -> function pointer
        self.app = []
        self.block: CommandBlock = None

    # blocks can't be created until after Commands objects, so must be added in a setter
    def set_block(self, block):
        self.block = block

    def command(self, name : str, info: str = "...", enable_input: bool = False):

        def decorator(f: callable):

            # basic wrapper
            def basic_wrapper(context):
                util.soup_log(f"[CMD] {name} {context.args if context.args else str()}")
                return f(self.block, context)

            # app wrapper
            if enable_input:
                async def app_wrapper(interaction: Interaction, enter:str=None):
                    args = []
                    if enter: args.extend(enter.split(" "))
                    util.soup_log(f"[CMD] {name} {args if args else str()}")
                    return await f(self.block, Context(args, interaction=interaction))
            else:
                async def app_wrapper(interaction: Interaction):
                    util.soup_log(f"[CMD] {name}")
                    return await f(self.block, Context([], interaction=interaction))

            self.basic[name] = basic_wrapper
            self.app.append(app_commands.command(name=name, description=info)(app_wrapper))

            return basic_wrapper
        return decorator


class CommandBlock:
    """meant to be subclassed in order to create commands for the discord bot"""

    name: str = "default"
    commands : Commands # each block subclass needs to make its own instance of Commands

    def __init__(self):
        # the commands object needs the block instance in order for its methods to be callable by the discord client
        self.commands.set_block(self)

    def close(self):
        pass


class CommandHandler:

    def __init__(self):
        self.blocks : [CommandBlock] = []

    def add_block(self, block: CommandBlock):
        self.blocks.append(block)
        util.soup_log(f"[BLK] block : {block.name} added")

    def make_command_tree(self, client):
        tree = app_commands.CommandTree(client)
        for b in self.blocks:
            for a in b.commands.app:
                tree.add_command(a)

        return tree

    def close(self):
        for b in self.blocks:
            b.close()

    def find_block(self, c):
        for i, b in enumerate(self.blocks):
            if c in b.commands.basic.keys():
                return i

        return -1

    def list_commands(self):
        c = []
        for b in self.blocks:
            c.extend(b.commands.basic.keys())
        return c

    def pass_command(self, block_index, cmd, context: Context):
        return self.blocks[block_index].commands.basic[cmd](context)
