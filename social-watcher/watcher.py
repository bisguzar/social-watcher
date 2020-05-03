import os
import json
import time
import models
from threading import Thread, Lock
from typing import Union, Dict

import telegram
from requests_html import HTML, HTMLSession
from pytablewriter import MarkdownTableWriter
from twitter_scraper import Profile

class FileNotFound(Exception):
    pass


class Stalker(object):
    def __init__(self):
        config_path = os.path.dirname(os.path.realpath(__file__))+"/configs.json"

        if not os.path.exists(config_path):
            raise FileNotFound("configs.json not found!")

        self.configs = json.loads(open(config_path).read())

        self.telegram = telegram.Bot(self.configs["telegram"]["token"])
        self.lock = Lock()

        self.session = HTMLSession()
        self.default_interval = self.configs.get("interval", 60 * 60)

    def start(self):
        if accounts := self.configs.get("twitter", None):
            for account in accounts:
                Thread(target=self.watch_twitter, args=(account,)).start()

        if accounts := self.configs.get("instagram", None):
            for account in accounts:
                Thread(target=self.watch_instagram, args=(account,)).start()

    def send_message(self, message):
        self.telegram.send_message(
            self.configs["telegram"]["chat_id"],
            message.replace(".", "\."),
            parse_mode=telegram.ParseMode.MARKDOWN_V2,
        )

    def watch_twitter(self, account: dict) -> None:
        current_data = Profile(account["username"]).to_dict()
        del current_data["username"]

        # change 'likes_count' to 'likes'
        for key,value in current_data.copy().items():
            if key.endswith("_count"):
                current_data[key.split("_")[0]] = value
                del current_data[key]

        last_data = (
            models.Twitter.select()
            .where(models.Twitter.username == account["username"])
            .order_by(-models.Twitter.timestamp)
            .limit(1)
        )

        if last_data:
            _changed_datas = self.__compare_datas(
                current_data, last_data[0], account.get("ignored_metrics", [])
            )

            if _changed_datas:
                table = self.__create_table(
                    "twitter", account["username"], _changed_datas
                )
                self.send_message(f"```\n {table} \n```")

            elif not account.get("only_if_changed", True):
                self.send_message(
                    f"Nothing changed for twitter/**{account['username']}**"
                )

        with self.lock:
            models.Twitter.create(username=account["username"], data=current_data)

        time.sleep(account.get("interval", self.default_interval))
        self.watch_twitter(account)

    def watch_instagram(self, account: dict) -> None:
        def _get_source():
            try:
                return HTMLSession().get(f"https://www.instagram.com/{account['username']}/").html
            except:
                _get_source()

        html = _get_source()
        data = json.loads(html.find("script[type='text/javascript']")[3].text[21:-1])
        data = data["entry_data"]["ProfilePage"][0]["graphql"]["user"]

        current_data = {
            "biography": data["biography"],
            "name": data["full_name"],
            "followers": data["edge_followed_by"]["count"],
            "following": data["edge_follow"]["count"],
            "posts": data["edge_owner_to_timeline_media"]["count"],
            "is_private": data["is_private"],
            "is_verified": data["is_verified"],
            "profile_photo": data["profile_pic_url_hd"],
        }

        with self.lock:
            last_data = (
                models.Instagram.select()
                .where(models.Instagram.username == account["username"])
                .order_by(-models.Instagram.timestamp)
                .limit(1)
            )

        if last_data:
            _changed_datas = self.__compare_datas(
                current_data, last_data[0], account.get("ignored_metrics", [])
            )

            if _changed_datas:
                table = self.__create_table(
                    "instagram", account["username"], _changed_datas
                )

                self.send_message(f"```\n {table} \n```")
            elif not account.get("only_if_changed", True):
                self.send_message(
                    f"Nothing changed for instagram/**{account['username']}**"
                )

        with self.lock:
            models.Instagram.create(username=account["username"], data=current_data)

        time.sleep(account.get("interval", self.default_interval))
        self.watch_instagram(account)

    def __compare_datas(
        self, current_data: dict, last_data: dict, ignored_metrics: list = []
    ) -> dict:
        _changed_datas = {}

        for key, value in current_data.items():
            if not value == last_data.data[key]:
                _changed_datas[key] = {
                    "last": last_data.data[key],
                    "last_timestamp": last_data.timestamp,
                    "current": current_data[key],
                }
                if key in (
                    "followers",
                    "following",
                    "posts",
                    "likes",
                    "tweets",
                ):
                    _changed_datas[key]["change"] = (
                        current_data[key] - last_data.data[key]
                    )

        for ignored_metric in ignored_metrics:
            if ignored_metric in _changed_datas:
                del _changed_datas[ignored_metric]

        return _changed_datas

    def __create_table(
        self, platform: str, username: str, changed_datas: Dict[str, Union[str, int]]
    ) -> str:
        table = MarkdownTableWriter()
        table.table_name = f"{platform.title()}: {username}"
        table.headers = ["Metric", "Value", "Change"]
        table.value_matrix = [
            [
                key,
                value["current"],
                value.get("change", "n/a")
                if value.get("change", False)
                else value["last"],
            ]
            for key, value in changed_datas.items()
        ]

        table.margin = 1

        return table.dumps()


if __name__ == "__main__":
    stalker = Stalker()
    stalker.start()
