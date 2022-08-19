#
# project imports
import commands

#
# util functions

# get commandHandler object
def get_command_handler():
    return commands.commandHandler

# cleanup cmd related processes before exit
def cleanup():
    commands.vc_commands.close()