#
# project imports
import general_commands
import time_commands
import vc_commands

#
# get commandHandler object
def get_command_handler():
    return general_commands.commandHandler

def cleanup():
    vc_commands.close()