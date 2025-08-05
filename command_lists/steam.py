import requests as _requests
import threading as _threading
import time as _time
import asyncio as _asyncio
from re import sub as _sub

import command_management.commands as _commands
import database.database_management.db_steam_apps as _db_steam_apps
import soup_util.constants as _constants
from soup_util.soup_logging import logger as _logger


_API_USE_COOLDOWN = 0.5


class CommandList(_commands.CommandList):

    name = "steam commands"

    async def on_start(self):
        _threading.Thread(target=_background_apps_refresh, daemon=True).start()

    async def on_close(self):
        pass

    @_commands.command("player-count", desc="Get the player count of a steam game")
    async def get_player_count(self, context, name: str):
        await context.defer_message()

        apps = await _asyncio.to_thread(_db_steam_apps.search, name, _make_searchable_name(name))

        if len(apps) == 0:
            await context.send_message(f"No steam games with the name *{name}*")
            return

        index_of_highest_priority = 0
        for i in range(len(apps)):
            if apps[index_of_highest_priority]["search_priority"] < apps[i]["search_priority"]:
                index_of_highest_priority = i

        app = apps[index_of_highest_priority]

        request = _requests.get(
            f"https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?appid={app['appid']}&format=json"
        )
        response = request.json()

        if "player_count" not in response["response"]:
            await context.send_message(f"No player count is currently available for the app *{app['name']}*")
            return

        await context.send_message(f"*{app['name']}* currently has {response['response']['player_count']} players online")


def _background_apps_refresh():
    HALF_HOUR = 1800
    MAX_APPS = 55

    if _db_steam_apps.is_empty():
        _fill_table(_get_apps())

    while True:
        start_time = _time.time()

        apps = _get_apps()
        app_ids = _db_steam_apps.get_all_app_ids()
        app_ids_in_need_of_update = _db_steam_apps.get_oldest_by_update_time(MAX_APPS)

        new_apps = []
        update_apps = []
        removed_from_steam = []

        for app in apps:
            if app["appid"] not in app_ids:
                new_apps.append(app)
            if app["appid"] in app_ids_in_need_of_update:
                update_apps.append(app)

        _fill_table(new_apps[:MAX_APPS] + update_apps[:max(0, MAX_APPS - len(new_apps))])

        for app_id in app_ids:
            if not any(x["appid"] == app_id for x in apps):
                removed_from_steam.append(app_id)

        _db_steam_apps.remove_all(removed_from_steam)

        _time.sleep(max(0.0, HALF_HOUR - (_time.time() - start_time)))

def _get_apps():
    temp_apps = []
    have_more_results = True
    last_appid = None

    while have_more_results:
        _time.sleep(_API_USE_COOLDOWN)

        request = _requests.get(
            f"https://api.steampowered.com/IStoreService/GetAppList/v1/?key={_constants.STEAM_API_KEY}"
            f"&include_games=true&max_results=50000&format=json"
            f"{f'&last_appid={last_appid}' if last_appid is not None else ''}"
        )
        response = request.json()

        if "apps" in response["response"].keys():
            temp_apps.extend(response["response"]["apps"])
            have_more_results = "have_more_results" in response["response"].keys()
            last_appid = response["response"].get("last_appid")

    return temp_apps

def _fill_table(apps):

    _logger.info("processing %s apps", len(apps))
    start_time = _time.time()

    for i, app in enumerate(apps):

        request = _requests.get(
            f"https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?appid={app['appid']}&format=json"
        )
        response = request.json()

        _db_steam_apps.add_or_update(
            app["appid"],
            app["name"],
            _make_searchable_name(app["name"]),
            -1 if not "player_count" in response["response"] else _search_prio(response['response']['player_count']),
            int(_time.time())
        )

        _time.sleep(_API_USE_COOLDOWN)

    _logger.info("finished processing apps in %.3f seconds", _time.time() - start_time)

def _make_searchable_name(name):
    return _sub("[^a-z0-9\s_]", "", name.lower())

def _search_prio(player_count):
    divisor = 100000.0 # very basic way of processing the player counts, as a more complex heuristic is overkill here
    return float(player_count) / divisor
