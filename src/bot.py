#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging
from collections import OrderedDict
from datetime import datetime, timedelta
from os.path import exists, join, realpath, dirname

import requests
import telebot

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
logger = logging.getLogger(__name__)

token = open(join(dirname(realpath(__file__)), 'secret.key'), 'r+').read()
bot = telebot.TeleBot(token)

VALID_COMMANDS = ['help', 'score', 'vote', 'meme', 'register']


@bot.message_handler(commands=['help'])
def help_info(message):
    chat_id = message.chat.id
    logger.info(f'Sending help to {chat_id}')
    bot.send_message(chat_id, '/help - Show this text' +
                     '\n/score - Display current MVP stats' +
                     '\n/vote *@username* - Vote username for MVP' +
                     '\n/meme - Generate meme for current MVP' +
                     '\n/register - Register to be eligible for MVP status')


@bot.message_handler(commands=['score'])
def score(message):
    chat_id = message.chat.id
    logger.info(f'Sending score to {chat_id}')
    scores = load_mvp_score(chat_id)
    scores = OrderedDict(reversed(sorted(scores.items(), key=lambda x: x[1])))
    if len(scores) == 0:
        bot.send_message(chat_id, 'No MVP list recorded for this chat group!')
    else:
        score_info = ''
        for k, v in scores.items():
            score_info += '*%s*: *%s*! ' % (fullname_by(k, chat_id), v)
        bot.send_message(chat_id, score_info)


@bot.message_handler(commands=['vote'])
def vote(message):
    chat_id = message.chat.id
    voter = message.from_user.username
    votee = message.text.split(' ')
    votes = load_vote_info(chat_id)

    if len(votee) < 2 or '@' not in votee[1]:
        bot.send_message(chat_id, 'You have to include @usertovotefor!')
    elif voter == '':
        bot.send_message(chat_id, 'Get a username first, before voting!')
    else:
        votee = votee[1].strip()[1:]
        logger.info(f'{voter} votes for {votee} in {chat_id}')
        if voter == votee or votee not in load_registered_users(chat_id):
            bot.send_message(chat_id, 'You can not vote for *%s*' % votee)
        elif voter in votes and ((datetime.now() - datetime.fromtimestamp(votes[voter])) < timedelta(days=1)):
            bot.send_message(chat_id, 'You already voted recently (24 hours)')
        else:
            scores = load_mvp_score(chat_id)
            scores[votee] = scores[votee] + 1 if votee in scores else 1
            bot.send_message(chat_id, '*%s* voted! MVP score *%s*: *%s*' %
                             (voter, fullname_by(votee, chat_id), scores[votee]))
            votes[voter] = (datetime.utcnow() - datetime(1970, 1, 1)).total_seconds()
            save_mvp_score(scores, chat_id)
            save_vote_info(votes, chat_id)


@bot.message_handler(commands=['meme'])
def meme(message):
    chat_id = message.chat.id
    logger.info(f'Generating meme for {chat_id}')
    image_link = requests.get("https://api.imgflip.com/"
                              "caption_image?template_id=15878567"
                              "&username=imgflip_hubot&password=imgflip_hubot"
                              "&text0=%s&text1=%s" % (
                                  real_mvp(chat_id).replace(' ', '%20'),
                                  'You%20Da%20Real%20MVP')).json()['data']['url']
    bot.send_message(chat_id, 'Congratulations! %s' % image_link)


@bot.message_handler(commands=['register'])
def register(message):
    chat_id = message.chat.id
    username = message.from_user.username
    fullname = f'{message.from_user.first_name} {message.from_user.last_name}'.strip()
    logger.info(f'Registering {fullname} as {username} from {chat_id}')
    if username != '':
        users = load_registered_users(chat_id)
        users[username] = fullname
        save_registered_users(users, chat_id)
        bot.send_message(chat_id, 'Thanks! *%s* registered as *%s*' % (fullname, username))
    else:
        bot.send_message(chat_id, 'Username can not be empty!')


@bot.message_handler(func=lambda message: is_invalid_command(message))
def unknown_command(message):
    chat_id = message.chat.id
    logger.info(f'Unknown command {message.text} in {chat_id}')
    bot.send_message(chat_id, text='That ain\'t no command!')


def real_mvp(chat_id):
    all_scores = load_mvp_score(chat_id)
    if len(all_scores) > 0:
        mvp = max(all_scores, key=all_scores.get)
        return '%s: %s' % (fullname_by(mvp, chat_id), all_scores[mvp])
    return 'NO ONE'


def is_invalid_command(message):
    return message.document.mime_type == 'text/plain' and \
           all(message.text.startswith('/') and not message.text.startswith(f'/{valid}') for valid in VALID_COMMANDS)


def fullname_by(username, chat_id):
    return load_registered_users(chat_id)[username]


def full_path_for(file, id):
    return join('data', '%s%s.json' % (file, id))


def create_if_not_exists(filename):
    if not exists(filename):
        open(filename, 'w+').write("{}")


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
    json.dump(content, open(filename, 'w+'))


def load(filename):
    create_if_not_exists(filename)
    return json.load(open(filename, 'r+'))


if __name__ == '__main__':
    logger.info('Starting bot...')
    bot.polling()
