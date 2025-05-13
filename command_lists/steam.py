import requests
import threading
from time import sleep, time
import re

from command_management import commands
from database.database_management import db_steam_apps
from soup_util import constants, soup_logging


_logger = soup_logging.get_logger()
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


def _fill_table(apps):

    def search_prio(pc):
        return float(pc) / 100000.0

    _logger.info("processing %s apps", len(apps))
    start_time = time()

    for i, app in enumerate(apps):

        request = requests.get(
            f"https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?appid={app['appid']}&format=json")
        response = request.json()

        db_steam_apps.add_or_update(
            app["appid"],
            app["name"],
            _make_searchable_name(app["name"]),
            -1 if not "player_count" in response["response"] else search_prio(response['response']['player_count']),
            int(time())
        )

    _logger.info("finished processing apps at %s seconds", time() - start_time)


def _background_apps_refresh(is_running):
    half_hour = 1800

    sleep(7) # wait for tables to be created in main thread

    if db_steam_apps.is_empty():
        _fill_table(_get_apps())

    while is_running():
        apps = _get_apps()
        app_ids = db_steam_apps.get_all_app_ids()
        app_ids_in_need_of_update = db_steam_apps.get_oldest_by_update_time(100)

        new_apps = []
        update_apps = []
        removed_from_steam = []

        for app in apps:
            if app["appid"] not in app_ids:
                new_apps.append(app)
            if app["appid"] in app_ids_in_need_of_update:
                update_apps.append(app)

        _fill_table(new_apps[:100] + update_apps)

        for app_id in app_ids:
            if not any(x["appid"] == app_id for x in apps):
                removed_from_steam.append(app_id)

        db_steam_apps.remove_all(removed_from_steam)

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

        apps = await context.run_blocking_func(db_steam_apps.search, name, _make_searchable_name(name))

        if len(apps) == 0:
            await context.send_message(f"No steam games with the name *{name}*")
            return

        index_of_highest_priority = 0
        for i in range(len(apps)):
            if apps[index_of_highest_priority]["search_priority"] < apps[i]["search_priority"]:
                index_of_highest_priority = i

        app = apps[index_of_highest_priority]

        request = requests.get(
            f"https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?appid={app['appid']}&format=json"
        )
        response = request.json()

        if "player_count" not in response["response"]:
            await context.send_message(f"No player count is currently available for the app *{app['name']}*")
            return

        await context.send_message(
            f"*{app['name']}* currently has {response['response']['player_count']} players online")
