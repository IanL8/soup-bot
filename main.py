from discord import Intents

from soup_bot_client import SoupBotClient
from soup_util.constants import TOKEN


if __name__ == "__main__":
    intents = Intents(guilds=True, voice_states=True, members=True, messages=True, message_content=True)
    client = SoupBotClient(intents=intents)
    client.run(TOKEN, log_handler=None)
