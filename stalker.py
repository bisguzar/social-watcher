import os
import json
import time
import models

import telegram
from dotenv import load_dotenv, find_dotenv
from requests_html import HTML, HTMLSession
from pytablewriter import MarkdownTableWriter


class Stalker(object):
    def __init__(self):
        load_dotenv(find_dotenv())

        self.telegram = telegram.Bot(os.getenv("STALKER_TELEGRAM_TOKEN"))
        self.chatid = os.getenv("STALKER_TELEGRAM_CHATID")

        self.session = HTMLSession()

        self.interval = int(os.getenv("STALKER_INTERVAL", 60))*60
        self.instagram_username = os.getenv("STALKER_INSTAGRAM", None)

    def start(self):
        if self.instagram_username:
            while True:
                self.watch_instagram()
                time.sleep(self.interval)

    def send_message(self, message):
        self.telegram.send_message(self.chatid, message, parse_mode=telegram.ParseMode.MARKDOWN_V2)

    def watch_instagram(self):
        html = HTMLSession().get(f"https://www.instagram.com/{self.instagram_username}/").html
        data = json.loads(html.find("script[type='text/javascript']")[3].text[21:-1])

        current_data = {
            "biography": data["entry_data"]["ProfilePage"][0]["graphql"]["user"]["biography"],
            "fullname": data["entry_data"]["ProfilePage"][0]["graphql"]["user"]["full_name"],
            "followers": data["entry_data"]["ProfilePage"][0]["graphql"]["user"]["edge_followed_by"]["count"],
            "following": data["entry_data"]["ProfilePage"][0]["graphql"]["user"]["edge_follow"]["count"],
            "posts": data["entry_data"]["ProfilePage"][0]["graphql"]["user"]["edge_owner_to_timeline_media"]["count"],
            "is_private": data["entry_data"]["ProfilePage"][0]["graphql"]["user"]["is_private"],
            "is_verified": data["entry_data"]["ProfilePage"][0]["graphql"]["user"]["is_verified"],
            "profile_picture": data["entry_data"]["ProfilePage"][0]["graphql"]["user"]["profile_pic_url_hd"]
        }

        last_data = (
            models.Instagram.select()
            .where(models.Instagram.username == self.instagram_username)
            .order_by(-models.Instagram.timestamp)
            .limit(1)
        )

        if last_data:
            # TODO: compare via last data
            last_timestamp = last_data[0].timestamp
            last_data = last_data[0].data

            _changed_datas = {}
            for key, value in current_data.items():
                if not value == last_data[key]:
                    _changed_datas[key] = {
                        'last': last_data[key],
                        'last_timestamp': last_timestamp,
                        'current': current_data[key]
                    }

                    if key in ('followers', 'following', 'posts'):
                        _changed_datas[key]['change'] = current_data[key] - last_data[key]

            if _changed_datas:
                table = MarkdownTableWriter()
                table.table_name = f"Instagram: {self.instagram_username}"
                table.headers = ["Key", "Value", "Change"]
                table.value_matrix = [
                    [
                        key, 
                        value["current"], 
                        value.get("change", "n/a")
                        if  
                        value.get("change", False)
                        else
                        value["last"]
                    ] 
                    for key, value in _changed_datas.items()
                ]

                table.margin = 1

                table = table.dumps()
                    
                self.send_message(f"```\n {table} \n```")
            else: 
                self.send_message(f"Nothing changed for instagram/**{self.instagram_username}**")

        models.Instagram.create(
            username=self.instagram_username,
            data=current_data
        )

if __name__ == "__main__":
    stalker = Stalker()
    stalker.start()