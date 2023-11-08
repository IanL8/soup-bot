from discord import Intents

from soup_bot_client import SoupBotClient
from soupbot_utilities import TOKEN


if __name__ == "__main__":
    intents = Intents.all()
    client = SoupBotClient(intents=intents)
    client.run(TOKEN)
