from discord import app_commands, Interaction, Message, Client

import soupbot_utilities as util


class Context:

    def __init__(self, args, message : Message = None, interaction : Interaction = None, bot : Client = None):

        if interaction is None:
            self.__interaction = None
            self.__message = message
            self.basic = True # basic cmd: True, app cmd: False
            self.bot = bot
            self.args = args
            self.channel = message.channel
            self.author = message.author
            self.guild = message.guild
            self.mentions = message.mentions
            self.voice_client = message.guild.voice_client
        else:
            self.__interaction = interaction
            self.__message = None
            self.basic = False
            self.bot = interaction.client
            self.args = args
            self.channel = interaction.channel
            self.author = interaction.user
            self.guild = interaction.guild
            self.mentions = []
            self.voice_client = interaction.guild.voice_client

            if "resolved" in interaction.data.keys():
                self.mentions = [self.guild.get_member(int(i)) for i in interaction.data["resolved"]["users"].keys()]

    async def send_message(self, s):
        if self.basic:
            msg = await self.channel.send(s)
        else:
            await self.__interaction.response.send_message(s)
            msg = await self.__interaction.original_response()

        return msg

    async def confirm(self):
        if self.basic:
            await self.__message.add_reaction("✅")
        else:
            await self.__interaction.response.send_message("✅")


class Commands:

    def __init__(self):
        self.cmds = dict()      # cmd name -> function pointer
        self.app_cmds = dict()  # cmd name -> function pointer
        self.block = None

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
                async def app_wrapper(interaction: Interaction, enter: str):
                    util.soup_log(f"[CMD] {name} {enter if not enter else enter.split()}")
                    return await f(self.block, Context(enter.split(" "), interaction=interaction))
            else:
                async def app_wrapper(interaction: Interaction):
                    util.soup_log(f"[CMD] {name}")
                    return await f(self.block, Context([], interaction=interaction))

            self.cmds[name] = basic_wrapper
            self.app_cmds[name] = app_commands.command(name=name, description=info)(app_wrapper)

            return basic_wrapper

        return decorator


class CommandBlock:

    name: str = "default"
    cmds : Commands # each block subclass needs to have its own copy of cmds

    def __init__(self):
        self.cmds.set_block(self)

    def close(self):
        pass


class CommandHandler:

    def __init__(self):
        self.blocks : [CommandBlock] = []

    def add_block(self, block: CommandBlock):
        self.blocks.append(block)
        util.soup_log(f"[BLK] block: {block.name} added")

    def make_command_tree(self, client):
        tree = app_commands.CommandTree(client)
        for b in self.blocks:
            for v in b.cmds.app_cmds.values():
                tree.add_command(v)

        return tree

    def close(self):
        for b in self.blocks:
            b.close()

    def find_block(self, c):
        for i, b in enumerate(self.blocks):
            if c in b.cmds.cmds.keys():
                return i

        return -1

    def list_commands(self):
        c = []
        for b in self.blocks:
            c.extend(b.cmds.cmds.keys())

    def pass_command(self, block_index, c, context: Context):
        return self.blocks[block_index].cmds.cmds[c](context)
