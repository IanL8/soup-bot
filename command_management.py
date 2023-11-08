from discord import app_commands, Interaction

import soupbot_utilities as util


class Context:
    def __init__(self, message=None, bot=None, args=None):

        self.__basic = True # basic cmd: True, app cmd: False
        self.__interaction = None
        self.__message = message

        self.bot = bot
        self.args = args

        if message:
            self.channel = message.channel
            self.author = message.author
            self.guild = message.guild
            self.mentions = message.mentions
            self.voice_client = message.guild.voice_client
        else:
            self.channel = None
            self.author = None
            self.guild = None
            self.mentions = None
            self.voice_client = None

    @staticmethod
    def copy_from_interaction(interaction, msg):
        c = Context()
        c.__basic = False
        c.__interaction = interaction
        c.__message = None
        c.channel = interaction.channel
        c.author = interaction.user
        c.guild = interaction.guild
        c.mentions = [c.guild.get_member(int(i)) for i in interaction.data["resolved"]["users"].keys()]
        c.voice_client = interaction.guild.voice_client
        c.bot = interaction.client
        c.args = msg.split(" ")

        return c

    async def send_message(self, s):
        if self.__basic:
            msg = await self.channel.send(s)
        else:
            await self.__interaction.response.send_message(s)
            msg = await self.__interaction.original_response()

        return msg

    async def confirm(self):
        if self.__basic:
            await self.__message.add_reaction("✅")
        else:
            await self.__interaction.response.send_message("✅")


class Commands:

    def __init__(self):
        self.cmds       = dict()    # cmd name -> function pointer
        self.app_cmds   = dict()    # cmd name -> function pointer
        self.block = None

    def set_block(self, block):
        self.block = block

    def command(self, name : str, info: str = "...", enable_input: bool = False):

        def decorator(f: callable):

            # basic wrapper
            def basic_wrapper(context):
                util.soup_log(f"[CMD] {name} {context.args if context.args else str()}")
                return f(self.block, context)

            # app wrapper
            async def app_wrapper(interaction: Interaction, enter: str):
                util.soup_log(f"[CMD] {name} {enter if not enter else enter.split()}")
                return await f(self.block, Context.copy_from_interaction(interaction, enter))

            self.cmds[name] = basic_wrapper
            self.app_cmds[name] = app_commands.command(name=name, description=info)(app_wrapper)

            return basic_wrapper

        return decorator


class CommandBlock:

    name: str = "default"
    cmds : Commands

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
