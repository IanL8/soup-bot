import requests
import threading
from time import sleep, time
import re

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
        temp_apps = _get_apps()
        _apps = temp_apps
        sleep(300)


threading.Thread(target=_background_apps_refresh, args=(lambda: _is_running,), daemon=True).start()


class CommandList(commands.CommandList):

    name = "steam commands"

    def on_close(self):
        global _is_running
        _is_running = False

    @commands.command("player-count", desc="Get the player count of a steam game")
    async def get_player_count(self, context, name: str):
        await context.defer_message()

        matches = []
        apps = _apps.copy()

        for app in apps:

            filtered_app_name = re.sub("[^a-z0-9\s_]", "", app["name"].lower())

            if name.lower() in filtered_app_name:

                request = requests.get(
                    f"https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?appid={app['appid']}&format=json")
                response = request.json()

                if "player_count" in response["response"]:

                    if name.lower () == filtered_app_name:
                        # if an exact match, return early

                        await context.send_message(f"*{app['name']}* currently has {response['response']['player_count']} players online")
                        return

                    matches.append((app["name"], response["response"]["player_count"]))

            if len(matches) == 15:
                break


        if len(matches) == 0:
            await context.send_message(f"no steam games with the name *{name}*")

        else:
            highest_player_count_index = -1

            for i in range(len(matches)):
                if matches[i][1] > matches[highest_player_count_index][1]:
                    highest_player_count_index = i

            app = matches[highest_player_count_index]

            await context.send_message(f"*{app[0]}* currently has {app[1]} players online")
