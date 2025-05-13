from discord import Intents

from soup_bot_client import SoupBotClient
from soup_util.constants import TOKEN


if __name__ == "__main__":
    intents = Intents.all()
    client = SoupBotClient(intents=intents)
    client.run(TOKEN, log_handler=None)
