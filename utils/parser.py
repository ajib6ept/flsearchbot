import urllib.request
import threading
import time
import datetime

import feedparser
import telegram

from .models import FLKey, FLProject


class FLParser():

    def __init__(self, settings, logger):
        self.settings = settings
        self.logger = logger

        pp = None
        if settings['proxy']:
            pp = telegram.utils.request.Request(proxy_url=settings['proxy'])
        self.bot = telegram.Bot(token=self.settings['token'], request=pp)

        proxy = self.settings.get('flproxy', None)
        if proxy:
            self.flproxy = [urllib.request.ProxyHandler({"http": proxy})]
        else:
            self.flproxy = None

        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True
        thread.start()

    def run(self):
        while True:
            self.logger.debug('Start fl parser')
            feed = feedparser.parse('https://www.fl.ru/rss/all.xml',
                                    handlers=self.flproxy)
            self.logger.debug(feed)
            for entry in feed['entries']:
                url = entry['link']
                title = entry['title_detail']['value']
                body = entry['summary']
                prj, created = FLProject.get_or_create(project_url=url,
                                                       project_title=title,
                                                       project_body=body)
                if created:
                    cur_time = datetime.datetime.now()
                    prj.project_added = cur_time
                    prj.save()
                    for key in FLKey.select():
                        if (key.name.lower() in body.lower() and
                                key.user.is_active):
                            msg = title + ' ' + url
                            self.bot.sendMessage(chat_id=key.user.telegram_id,
                                                 text=msg)
                            self.logger.debug(
                                'Send message "%s" to %s' % (msg, key.user))
            time.sleep(self.settings['interval'])
