import os
import json
import click

from typing import Union
from social_watcher.watcher import Watcher

_header = """ 
 _____            _       _          _    _       _       _               
/  ___|          (_)     | |        | |  | |     | |     | |              
\ `--.  ___   ___ _  __ _| | ______ | |  | | __ _| |_ ___| |__   ___ _ __ 
 `--. \/ _ \ / __| |/ _` | | ______ | |/\| |/ _` | __/ __| '_ \ / _ \ '__|
/\__/ / (_) | (__| | (_| | |        \  /\  / (_| | || (__| | | |  __/ |   
\____/ \___/ \___|_|\__,_|_|         \/  \/ \__,_|\__\___|_| |_|\___|_|
"""


def _get_input(
    label: str,
    is_bool: bool = False,
    default: Union[str, int] = None,
    type: Union[str, int, list] = None,
) -> str:

    _input = lambda: input(
        "{label}{options}{default}: ".format(
            label=label,
            options=" (y/n)" if is_bool else "",
            default=" (default: {})".format(default) if default else "",
        )
    )
    answer = _input()

    if default and not answer:
        return default

    while True:
        if is_bool:
            if answer not in ("y", "n"):
                print("[!] Please enter valid option.")
                answer = _input()
                continue
            else:
                return True if answer == "y" else False

        elif not answer:
            print("[!] You can not leave blank.")
            answer = _input()
            continue

        if type == int:
            return int(answer)

        return answer


def _configure() -> None:
    print(_header)

    config_schema = {
        "interval": _get_input(
            "Enter global interval as seconds", default=86400, type=int
        ),
        "database": _get_input("Enter full path of sqlite database"),
        "instagram": [],
        "twitter": [],
    }

    if _get_input("Enable telegram", is_bool=True):
        config_schema["telegram"] = {
            "token": _get_input("Enter telegram bot token"),
            "chat_id": _get_input("Enter telegram chat id"),
        }

    add_account = lambda: {
        "username": _get_input("Username"),
        "interval": _get_input(
            "Spesific interval for this account as seconds",
            default=config_schema["interval"],
            type=int,
        ),
        "only_if_changed": not _get_input(
            "Do you want to be warned even if no changes (only works when telegram configured)",
            is_bool=True,
        ),
        "ignored_metrics": [],
    }

    while _get_input(
        "Would you like to add another instagram account to watch list?"
        if config_schema["instagram"]
        else "Would you like to add instagram account to watch list?",
        is_bool=True,
    ):
        config_schema["instagram"].append(add_account())

    while _get_input(
        "Would you like to add another twitter account to watch list?"
        if config_schema["twitter"]
        else "Would you like to add twitter account to watch list?",
        is_bool=True,
    ):
        config_schema["twitter"].append(add_account())

    with open("watcher.json", "w") as file:
        file.write(json.dumps(config_schema, indent=4))


@click.command()
@click.option("--configure", help="Create a configuration file.", is_flag=True)
@click.option("--config", help="Full path of configuration file")
def main(configure, config):
    if configure:
        _configure()
        return

    if not config or not os.path.exists(config):
        print("Config file not exists, please specify full path.")
        print("Use --help parameter for available parameters.")
        return

    configs = json.loads(open(config).read())
    watcher = Watcher(configs)
    watcher.start()


if __name__ == "__main__":
    main()
