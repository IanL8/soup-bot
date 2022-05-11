#
# imports
import os
from discord import Intents
from dotenv import load_dotenv

#
# project imports
from soup_bot_client import SoupBotClient

#
# get .env values
load_dotenv("values.env")
TOKEN = os.getenv("DISCORD_TOKEN")

if __name__ == "__main__":
    intents = Intents.all()
    client = SoupBotClient(intents=intents)
    client.run(TOKEN)
