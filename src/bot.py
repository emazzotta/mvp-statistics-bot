#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging
from collections import OrderedDict
from os.path import exists, join, realpath, dirname

from telegram import ParseMode
from telegram.ext import Updater

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
logger = logging.getLogger(__name__)


def fullname_by(username, chat_id):
    return registered_users(chat_id)[username]


def fullpath_for(file, id):
    return join('data', '%s%s.json' % (file, id))


def create_if_not_exists(filename):
    if not exists(filename):
        with open(filename, 'w+') as data_file:
            data_file.write("{}")


def mvp_score(chat_id):
    filename = fullpath_for('scores', chat_id)
    create_if_not_exists(filename)
    with open(filename, 'r+') as score_file:
        scores = json.load(score_file)
    return scores


def save_mvp_score(scores, chat_id):
    filename = fullpath_for('scores', chat_id)
    create_if_not_exists(filename)
    with open(filename, 'w+') as score_file:
        json.dump(scores, score_file)


def registered_users(chat_id):
    filename = fullpath_for('users', chat_id)
    create_if_not_exists(filename)
    with open(filename, 'r+') as user_file:
        registered = json.load(user_file)
    return registered


def save_registered_users(users, chat_id):
    filename = fullpath_for('users', chat_id)
    create_if_not_exists(filename)
    with open(filename, 'w+') as user_file:
        json.dump(users, user_file)


def score(bot, update):
    scores = mvp_score(update.message.chat_id)
    scores = OrderedDict(reversed(sorted(scores.items(), key=lambda x: x[1])))
    for k, v in scores.items():
        bot.sendMessage(update.message.chat_id,
                        text='MVP score for *%s*: *%s*' % (
                            fullname_by(k, update.message.chat_id), v),
                        parse_mode=ParseMode.MARKDOWN)


def help(bot, update):
    bot.sendMessage(update.message.chat_id,
                    text='/help - Show this text' +
                         '\n/score - Display current MVP stats' +
                         '\n/vote *@username* - Vote username for MVP' +
                         '\n/register - Register to be eligible for MVP status',
                    parse_mode=ParseMode.MARKDOWN)


def vote(bot, update):
    voter = update.message.from_user.username
    votee = update.message.text.split(' ')[1].strip()[1:]

    if voter == votee or votee not in registered_users(update.message.chat_id):
        bot.sendMessage(update.message.chat_id,
                        text="You can not vote for *%s*" % votee,
                        parse_mode=ParseMode.MARKDOWN)
    else:
        scores = mvp_score(update.message.chat_id)
        scores[votee] = scores[votee] + 1 if votee in scores else 1
        save_mvp_score(scores, update.message.chat_id)
        bot.sendMessage(update.message.chat_id,
                        text='*%s* voted! MVP score for *%s*: *%s*' %
                             (voter, fullname_by(votee, update.message.chat_id),
                              scores[votee]),
                        parse_mode=ParseMode.MARKDOWN)


def register(bot, update):
    username = update.message.from_user.username
    fullname = ("%s %s" % (update.message.from_user.first_name,
                           update.message.from_user.last_name)).strip()
    if username != '':
        users = registered_users(update.message.chat_id)
        users[username] = fullname
        save_registered_users(users, update.message.chat_id)
        bot.sendMessage(update.message.chat_id,
                        text='Thanks! *%s* registered as *%s*' % (
                            fullname, username),
                        parse_mode=ParseMode.MARKDOWN)
    else:
        bot.sendMessage(update.message.chat_id,
                        text='Username can not be empty!',
                        parse_mode=ParseMode.MARKDOWN)


def unknown_command(bot, update):
    bot.sendMessage(update.message.chat_id, text='That ain\'t no command!')


def error(update, error):
    logger.warn('Update %s caused error %s' % (update, error))


def main():
    with open(join(dirname(realpath(__file__)), "secret.key"), 'r+') as secret_file:
        token = secret_file.read()
    updater = Updater(token, workers=10)
    dp = updater.dispatcher
    dp.addTelegramCommandHandler("score", score)
    dp.addTelegramCommandHandler("help", help)
    dp.addTelegramCommandHandler("vote", vote)
    dp.addTelegramCommandHandler("register", register)
    dp.addUnknownTelegramCommandHandler(unknown_command)
    dp.addErrorHandler(error)
    update_queue = updater.start_polling(poll_interval=0.1, timeout=10)
    while True:
        text = input()
        update_queue.put(text)


if __name__ == '__main__':
    main()

