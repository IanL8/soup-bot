import requests
import threading
from time import sleep

from command_management import commands
from soupbot_util import constants


_apps = []
_is_running = True

def _get_apps():
    request = requests.get(
        f"https://api.steampowered.com/IStoreService/GetAppList/v1/?key={constants.STEAM_API_KEY}"
        f"&include_games=true&max_results=50000&format=json")

    response = request.json()
    have_more_results = True

    temp_apps = response["response"]["apps"]

    while have_more_results:
        request = requests.get(
            f"https://api.steampowered.com/IStoreService/GetAppList/v1/"
            f"?key={constants.STEAM_API_KEY}&include_games=true&max_results=50000"
            f"&last_appid={response['response']['last_appid']}&format=json")

        response = request.json()
        temp_apps.extend(response["response"]["apps"])
        have_more_results = response["response"].get("have_more_results")

    return temp_apps

def _background_apps_refresh(is_running):
    global _apps

    while is_running():
        _apps = _get_apps()
        sleep(300)


threading.Thread(target=_background_apps_refresh, args=(lambda: _is_running,), daemon=True).start()


class CommandList(commands.CommandList):

    name = "steam commands"

    def on_close(self):
        global _is_running
        _is_running = False

    @commands.command("player-count", desc="Get the player count of a steam game")
    async def get_player_count(self, context, name: str):
        matches = []

        for app in _apps:
            if name.lower() in app["name"].lower():
                request = requests.get(f"https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?appid={app['appid']}&format=json")
                response = request.json()
                if "player_count" in response["response"]:
                    matches.append((app["name"], response["response"]["player_count"]))

        matches.sort(key=lambda x: x[1], reverse=True)

        if len(matches) == 0:
            await context.send_message(f"no steam games with the name *{name}*")
        else:
            app = matches[0]
            await context.send_message(f"*{app[0]}* currently has {app[1]} players online")
