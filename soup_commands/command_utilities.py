#
# imports
from discord import app_commands

#
# project imports
import soup_commands

#
# util functions

# get commandHandler object
def get_command_handler():
    return soup_commands.commandHandler


#make command tree
def make_command_tree(client):
    tree = app_commands.CommandTree(client)
    for v in soup_commands.commandHandler.appCMDs.values():
        tree.add_command(v)

    return tree


# cleanup cmd related processes before exit
def cleanup():
    soup_commands.vc_commands.close()