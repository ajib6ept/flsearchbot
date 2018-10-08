import os
import json

from telegram.ext import Updater, CommandHandler

from utils.models import User, FLKey
from utils.logger import Logger
from utils.parser import FLParser
from utils.tools import is_key_correct


class FLBot():

    def __init__(self):

        # settings
        with open('settings.json') as f:
            self.settings = json.load(f)

        # add logger
        path = os.path.dirname(os.path.realpath(__file__))
        log_file = path + self.settings['log_path']
        self.logger = Logger(log_file, 'flbot').get()

        proxy = self.settings['proxy']
        kwargs = {'proxy_url': proxy} if proxy else None

        self.updater = Updater(token=self.settings['token'],
                               request_kwargs=kwargs)

        # Add commands
        self._add_command(CommandHandler("start", self.start))
        self._add_command(CommandHandler("add", self.add,
                                         pass_args=True))
        self._add_command(CommandHandler("remove", self.remove,
                                         pass_args=True))
        self._add_command(CommandHandler("list", self.list))
        self._add_command(CommandHandler("help", self.help))
        self._add_command(CommandHandler("stop", self.stop))

        # Start bot
        self.logger.debug('Start FLBot!')
        self.parser = FLParser(settings=self.settings, logger=self.logger)
        self.updater.start_polling()
        self.updater.idle()

    def _add_command(self, command):
        self.updater.dispatcher.add_handler(command)

    def start(self, bot, update):
        telegram_user = update.message.from_user
        if not User.get_or_none(telegram_id=telegram_user.id):
            User.create(telegram_id=telegram_user.id,
                        username=telegram_user.username,
                        firstname=telegram_user.first_name,
                        lastname=telegram_user.last_name)
            msg = 'Привет, этот бот поможет быстро получать информацию ' \
                  'о новых проектах на fl.ru'
            update.message.reply_text(msg)
        else:
            User.update(is_active=True).where(
                User.telegram_id == telegram_user.id).execute()
            msg = 'Сообщения теперь будут приходить'
            update.message.reply_text(msg)
        msg = 'Я готов отправлять сообщение, /help для помощи'
        self.logger.debug('/start command form user %s' % telegram_user)
        update.message.reply_text(msg)

    def is_correct_len_key(self, args):
        return (4 > len(args[0])) and (13 > len(args[0]))

    def add(self, bot, update, args):
        if not args:
            msg = 'Нет слов для добавляния, /help для помощи'
            update.message.reply_text(msg)
            return
        elif len(args) != 1:
            msg = 'Можно добавить только одно слово, /help для помощи'
            update.message.reply_text(msg)
            return
        elif not is_key_correct(args[0]):
            msg = 'Некорретный формат ключа, /help для помощи'
            update.message.reply_text(msg)
            return
        telegram_user = update.message.from_user
        key, created = FLKey.get_or_create(user=telegram_user.id, name=args[0])
        if created:
            msg = 'Ключ успешно добавлен'
        else:
            msg = 'Ключ уже был в списке'
        self.logger.debug('/add "%s" command form user %s' %
                          (key, telegram_user))
        update.message.reply_text(msg)

    def remove(self, bot, update, args):
        if not args:
            msg = 'Нет слов для удаления, /help для помощи'
            update.message.reply_text(msg)
            return
        if len(args) != 1:
            msg = 'Слишком длинный параметр, /help для помощи'
            update.message.reply_text(msg)
            return
        telegram_user = update.message.from_user
        key = FLKey.get_or_none(user=telegram_user.id, name=args[0])
        if key is None:
            msg = 'Ключ не найден'
        else:
            key.delete_instance()
            msg = 'Ключ "%s" удален из поиска' % key.key
        self.logger.debug('/remove "%s" command form user %s' %
                          (key, telegram_user))
        update.message.reply_text(msg)

    def list(self, bot, update):
        telegram_user = update.message.from_user
        flkeys = FLKey.select().where(FLKey.user == telegram_user.id)
        keys = [k.name for k in flkeys]
        if keys:
            msg = 'Список ключей:\n'
            for k, v in enumerate(keys, start=1):
                msg += '%s) %s\n' % (k, v)
        else:
            msg = 'Ключи не найдены'
        self.logger.debug('/list command form user %s' % telegram_user)
        update.message.reply_text(msg)

    def help(self, bot, update):
        telegram_user = update.message.from_user
        msg = 'Тут будет страница помощи'
        self.logger.debug('/help command form user %s' % telegram_user)
        update.message.reply_text(msg)

    def stop(self, bot, update):
        telegram_user = update.message.from_user
        User.update(is_active=False).where(
            User.telegram_id == telegram_user.id).execute()
        msg = "Стоп сообщениям"
        self.logger.debug('/stop command form user %s' % telegram_user)
        update.message.reply_text(msg)


if __name__ == '__main__':
    FLBot()
