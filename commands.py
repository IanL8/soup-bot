#
# project imports
from command_categories import commandHandler, general_commands, vc_commands, time_commands

#
# get commandHandler object
def get_command_handler():
    return commandHandler

def cleanup():
    vc_commands.close()