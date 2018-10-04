
import json
import threading
import time

import feedparser
import telegram

from utils.models import FLKey, FLProject

with open('settings.json') as f:
    settings = json.load(f)
token = settings['token']
proxy = settings['proxy']

INTERVAL = 30


class FLParser():

    def __init__(self, logger):
        self.logger = logger
        pp = telegram.utils.request.Request(proxy_url=proxy)
        self.bot = telegram.Bot(token=token, request=pp)

        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True
        thread.start()

    def run(self):
        while True:
            keys = [k.name for k in FLKey.select()]
            feed = feedparser.parse('https://www.fl.ru/rss/all.xml')
            for entry in feed['entries']:
                entry_url = entry['link']
                entry_title = entry['title_detail']['value']
                entry_body = entry['summary']
                prj, created = FLProject.get_or_create(project_url=entry_url,
                                                       project_title=entry_title,
                                                       project_body=entry_body)
                if created:
                    for key in FLKey.select():
                        if key.name.lower() in entry_body.lower() and key.user.is_active:
                            msg = entry_title + ' ' + entry_url
                            self.bot.sendMessage(chat_id=key.user.telegram_id,
                                                 text=msg)
                            self.logger.debug(
                                'Send message "%s" to %s' % (msg, key.user))
            time.sleep(INTERVAL)
