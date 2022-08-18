#
# project imports
from command_categories import general_commands, vc_commands, time_commands


#
# get commandHandler object
def get_command_handler():
    return general_commands.commandHandler

def cleanup():
    vc_commands.close()