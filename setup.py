#
# imports
from os import getenv
from dotenv import load_dotenv
from discord import Intents

#
# project imports
from soup_bot_client import SoupBotClient

#
# get .env values
load_dotenv("values.env")
TOKEN = getenv("DISCORD_TOKEN")

if __name__ == "__main__":
    intents = Intents.all()
    client = SoupBotClient(intents=intents)
    client.run(TOKEN)
