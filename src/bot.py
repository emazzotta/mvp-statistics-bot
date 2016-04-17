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


def score(bot, update):
    chat_id = update.message.chat_id
    scores = mvp_score(chat_id)
    scores = OrderedDict(reversed(sorted(scores.items(), key=lambda x: x[1])))
    if len(scores) == 0:
        send_message(bot, chat_id, 'No MVP list recorded for this chat group!')
    else:
        score_info = ''
        for k, v in scores.items():
            score_info += '*%s*: *%s*! ' % (fullname_by(k, chat_id), v)
        send_message(bot, chat_id, score_info)


def help(bot, update):
    send_message(bot, update.message.chat_id, '/help - Show this text' +
                 '\n/score - Display current MVP stats' +
                 '\n/vote *@username* - Vote username for MVP' +
                 '\n/register - Register to be eligible for MVP status')


def vote(bot, update):
    chat_id = update.message.chat_id
    voter = update.message.from_user.username
    votee = update.message.text.split(' ')

    if len(votee) < 2 or '@' not in votee[1]:
        send_message(bot, chat_id,
                     'Your vote is unclear, you have to include @usertovotefor')
    else:
        votee = votee[1].strip()[1:]
        if voter == votee or votee not in registered_users(chat_id):
            send_message(bot, chat_id, 'You can not vote for *%s*' % votee)
        else:
            scores = mvp_score(chat_id)
            scores[votee] = scores[votee] + 1 if votee in scores else 1
            save_mvp_score(scores, chat_id)
            send_message(bot, chat_id, '*%s* voted! MVP score for *%s*: *%s*' %
                         (voter, fullname_by(votee, chat_id), scores[votee]))


def register(bot, update):
    username = update.message.from_user.username
    fullname = ("%s %s" % (update.message.from_user.first_name,
                           update.message.from_user.last_name)).strip()
    chat_id = update.message.chat_id
    if username != '':
        users = registered_users(chat_id)
        users[username] = fullname
        save_registered_users(users, chat_id)
        send_message(bot, chat_id,
                     'Thanks! *%s* registered as *%s*' % (fullname, username))
    else:
        send_message(bot, chat_id, 'Username can not be empty!')


def unknown_command(bot, update):
    bot.sendMessage(update.message.chat_id, text='That ain\'t no command!')


def error(update, error):
    logger.warn('Update %s caused error %s' % (update, error))


def main():
    key_path = join(dirname(realpath(__file__)), 'secret.key')
    with open(key_path, 'r+') as secret_file:
        token = secret_file.read()
    updater = Updater(token, workers=10)
    dispatcher = updater.dispatcher
    dispatcher.addTelegramCommandHandler("score", score)
    dispatcher.addTelegramCommandHandler("help", help)
    dispatcher.addTelegramCommandHandler("vote", vote)
    dispatcher.addTelegramCommandHandler("register", register)
    dispatcher.addUnknownTelegramCommandHandler(unknown_command)
    dispatcher.addErrorHandler(error)
    update_queue = updater.start_polling(poll_interval=0.1, timeout=10)
    while True:
        text = input()
        update_queue.put(text)


def fullname_by(username, chat_id):
    return registered_users(chat_id)[username]


def full_path_for(file, id):
    return join('data', '%s%s.json' % (file, id))


def create_if_not_exists(filename):
    if not exists(filename):
        with open(filename, 'w+') as data_file:
            data_file.write("{}")


def mvp_score(chat_id):
    filename = full_path_for('scores', chat_id)
    create_if_not_exists(filename)
    with open(filename, 'r+') as score_file:
        scores = json.load(score_file)
    return scores


def save_mvp_score(scores, chat_id):
    filename = full_path_for('scores', chat_id)
    create_if_not_exists(filename)
    with open(filename, 'w+') as score_file:
        json.dump(scores, score_file)


def registered_users(chat_id):
    filename = full_path_for('users', chat_id)
    create_if_not_exists(filename)
    with open(filename, 'r+') as user_file:
        registered = json.load(user_file)
    return registered


def save_registered_users(users, chat_id):
    filename = full_path_for('users', chat_id)
    create_if_not_exists(filename)
    with open(filename, 'w+') as user_file:
        json.dump(users, user_file)


def send_message(bot, chat_id, text):
    bot.sendMessage(chat_id, text=text, parse_mode=ParseMode.MARKDOWN)


if __name__ == '__main__':
    main()
