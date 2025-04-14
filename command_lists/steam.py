import requests
import threading
from time import sleep, time
import re

from command_management import commands
from database.database_management import db_steam_apps, db_steam_app_table_refreshes
from soupbot_util import constants
from soupbot_util.logger import soup_log

_is_running = True


def _make_searchable_name(name):
    return re.sub("[^a-z0-9\s_]", "", name.lower())


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
            f"&last_appid={response['response']['last_appid']}&format=json"
        )
        response = request.json()

        temp_apps.extend(response["response"]["apps"])
        have_more_results = response["response"].get("have_more_results")

    return temp_apps


def _refresh(apps, start_time):

    def search_prio(pc):
        return float(pc) / 100000.0

    progress_display = [.1, .2, .3, .4, .5, .6, .7, .8, .9, .95, .96, .97, .98, .99, 1]

    for i, app in enumerate(apps):

        request = requests.get(
            f"https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?appid={app['appid']}&format=json")
        response = request.json()

        if "player_count" in response["response"]:
            db_steam_apps.add_or_update(
                app["appid"],
                app["name"],
                _make_searchable_name(app["name"]),
                search_prio(response['response']['player_count'])
            )

            db_steam_app_table_refreshes.update_last_app_id(start_time, app["appid"])

        while len(progress_display) > 0 and progress_display[0] < float(i+1) / len(apps):
            soup_log(f"Steam app processing {int(progress_display.pop(0) * 100)}% of the way done", "APP")

    db_steam_app_table_refreshes.mark_refresh_complete(start_time)
    soup_log(f"Steam apps search priority update finished", "APP")

def _background_apps_refresh(is_running):
    four_months = 10713600
    half_hour = 1800

    sleep(7) # wait for tables to be created in main thread

    if db_steam_apps.is_empty():

        start_time = int(time())
        db_steam_app_table_refreshes.add(start_time)
        _refresh(_get_apps(), start_time)

    incomplete_refresh_start_time = db_steam_app_table_refreshes.get_incomplete_refresh_start_time()

    if incomplete_refresh_start_time is not None:

        apps = _get_apps()
        last_app_id = db_steam_app_table_refreshes.get_last_app_id(incomplete_refresh_start_time)
        index = 0

        for i in range(len(apps)):
            if apps[i]["appid"] == last_app_id:
                index = i
                break

        _refresh(apps[index+1:], incomplete_refresh_start_time)

    while is_running():
        apps = _get_apps()

        if time() - db_steam_app_table_refreshes.get_latest_refresh_start_time() > four_months:
            start_time = int(time())
            db_steam_app_table_refreshes.add(start_time)
            _refresh(apps, start_time)

        app_ids = db_steam_apps.get_all_app_ids()
        new_apps = []
        removed_from_steam = []

        # check and add any apps that are new to steam
        for app in apps:
            if app["appid"] not in app_ids:
                new_apps.append(app)



        # remove apps that are no longer on steam

        sleep(half_hour)


threading.Thread(target=_background_apps_refresh, args=(lambda: _is_running,), daemon=True).start()


class CommandList(commands.CommandList):

    name = "steam commands"

    def on_close(self):
        global _is_running
        _is_running = False

    @commands.command("player-count", desc="Get the player count of a steam game")
    async def get_player_count(self, context, name: str):
        await context.defer_message()

        app = db_steam_apps.search(name, _make_searchable_name(name))

        if app is None:
            await context.send_message(f"no steam games with the name *{name}*")
            return

        request = requests.get(
            f"https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?appid={app['appid']}&format=json"
        )
        response = request.json()

        if "player_count" not in response["response"]:
            await context.send_message(f"Error getting player count for *{app['name']}*")
            return

        await context.send_message(f"*{app['name']}* currently has {response['response']['player_count']} players online")
