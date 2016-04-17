#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging
from collections import OrderedDict
from datetime import datetime, timedelta
from os.path import exists, join, realpath, dirname

import requests
from telegram import ParseMode
from telegram.ext import Updater

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    key_path = join(dirname(realpath(__file__)), 'secret.key')
    with open(key_path, 'r+') as secret_file:
        token = secret_file.read()
    updater = Updater(token, workers=10)
    dispatcher = updater.dispatcher
    dispatcher.addTelegramCommandHandler("score", score)
    dispatcher.addTelegramCommandHandler("help", help)
    dispatcher.addTelegramCommandHandler("vote", vote)
    dispatcher.addTelegramCommandHandler("meme", meme)
    dispatcher.addTelegramCommandHandler("register", register)
    dispatcher.addUnknownTelegramCommandHandler(unknown_command)
    dispatcher.addErrorHandler(error)
    update_queue = updater.start_polling(poll_interval=0.1, timeout=10)
    while True:
        text = input()
        update_queue.put(text)


def help(bot, update):
    send_message(bot, update.message.chat_id, '' +
                 '/help - Show this text' +
                 '\n/score - Display current MVP stats' +
                 '\n/vote *@username* - Vote username for MVP' +
                 '\n/meme - Generate meme for current MVP' +
                 '\n/register - Register to be eligible for MVP status')


def score(bot, update):
    chat_id = update.message.chat_id
    scores = load_mvp_score(chat_id)
    scores = OrderedDict(reversed(sorted(scores.items(), key=lambda x: x[1])))
    if len(scores) == 0:
        send_message(bot, chat_id, 'No MVP list recorded for this chat group!')
    else:
        score_info = ''
        for k, v in scores.items():
            score_info += '*%s*: *%s*! ' % (fullname_by(k, chat_id), v)
        send_message(bot, chat_id, score_info)


def vote(bot, update):
    chat_id = update.message.chat_id
    voter = update.message.from_user.username
    votee = update.message.text.split(' ')
    votes = load_vote_info(chat_id)

    if len(votee) < 2 or '@' not in votee[1]:
        send_message(bot, chat_id, 'You have to include @usertovotefor!')
    elif voter == '':
        send_message(bot, chat_id, 'Get a username first, before voting!')
    else:
        votee = votee[1].strip()[1:]
        if voter == votee or votee not in load_registered_users(chat_id):
            send_message(bot, chat_id, 'You can not vote for *%s*' % votee)
        elif voter in votes and ((datetime.now() - datetime.fromtimestamp(votes[voter])) < timedelta(days=1)):
            send_message(bot, chat_id, 'You already voted recently (24 hours)')
        else:
            scores = load_mvp_score(chat_id)
            scores[votee] = scores[votee] + 1 if votee in scores else 1
            send_message(bot, chat_id, '*%s* voted! MVP score *%s*: *%s*' %
                         (voter, fullname_by(votee, chat_id), scores[votee]))
            votes[voter] = (datetime.utcnow() - datetime(1970, 1, 1)).total_seconds()
            save_mvp_score(scores, chat_id)
            save_vote_info(votes, chat_id)


def real_mvp(chat_id):
    all = load_mvp_score(chat_id)
    if len(all) > 0:
        mvp = ''
        for k, v in all.items():
            if mvp == '' or mvp[0] < v:
                mvp = {k: v}
        return '%s: %s' % (fullname_by(k, chat_id), v)
    else:
        return 'NO ONE'


def meme(bot, update):
    chat_id = update.message.chat_id
    image_link = requests.get("https://api.imgflip.com/"
                             "caption_image?template_id=15878567"
                             "&username=imgflip_hubot&password=imgflip_hubot"
                             "&text0=%s&text1=%s" % (
        real_mvp(chat_id).replace(' ', '%20'),
        'You%20Da%20Real%20MVP')).json()['data']['url']
    send_message(bot, chat_id, 'Congratulations! %s' % image_link)


def register(bot, update):
    username = update.message.from_user.username
    fullname = ("%s %s" % (update.message.from_user.first_name,
                           update.message.from_user.last_name)).strip()
    chat_id = update.message.chat_id
    if username != '':
        users = load_registered_users(chat_id)
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


def fullname_by(username, chat_id):
    return load_registered_users(chat_id)[username]


def full_path_for(file, id):
    return join('data', '%s%s.json' % (file, id))


def create_if_not_exists(filename):
    if not exists(filename):
        with open(filename, 'w+') as data_file:
            data_file.write("{}")


def load_mvp_score(chat_id):
    return load(full_path_for('scores', chat_id))


def load_registered_users(chat_id):
    return load(full_path_for('users', chat_id))


def load_vote_info(chat_id):
    return load(full_path_for('votes', chat_id))


def save_mvp_score(scores, chat_id):
    save(full_path_for('scores', chat_id), scores)


def save_registered_users(users, chat_id):
    save(full_path_for('users', chat_id), users)


def save_vote_info(votes, chat_id):
    save(full_path_for('votes', chat_id), votes)


def save(filename, content):
    create_if_not_exists(filename)
    with open(filename, 'w+') as write_file:
        json.dump(content, write_file)


def load(filename):
    create_if_not_exists(filename)
    with open(filename, 'r+') as load_file:
        loaded_data = json.load(load_file)
    return loaded_data


def send_message(bot, chat_id, text):
    bot.sendMessage(chat_id, text=text, parse_mode=ParseMode.MARKDOWN)


if __name__ == '__main__':
    main()
