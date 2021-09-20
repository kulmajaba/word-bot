# coding: utf-8

import csv
import threading
from datetime import date, datetime, timedelta
from os import environ
from typing import Union

from telegram import (
  Bot,
  CallbackQuery,
  InlineKeyboardButton,
  InlineKeyboardMarkup,
  KeyboardButton,
  ReplyKeyboardMarkup,
  TelegramError,
  Update
) 
from telegram.ext import (
  CallbackContext,
  CallbackQueryHandler,
  CommandHandler,
  Filters,
  MessageHandler,
  Updater
)
import psycopg2

from db_psql import DatabasePsql
from strings import strings

import utils


# -----------------------------------------------------------------------------

def start(update: Update, context: CallbackContext):
  chat_id, _, _ = utils.update_get_ids(update)
  bot: Bot = context.bot

  msg = "{}".format(strings["start"])
  bot.send_message(chat_id=chat_id, text=msg)

def add_ari_word(update: Update, context: CallbackContext):
  chat_id, user_id, _ = utils.update_get_ids(update)
  bot: Bot = context.bot

  # No argument?
  if (len(context.args) == 0):
    update.message.reply_text(strings["command_sana_no_word"])
    return

  word = context.args[0].lower()

  try:
    result = db.insert_ari_word(word, False)
    msg = strings["word_added"]
    bot.send_message(chat_id=chat_id, text=msg)
  except psycopg2.errors.UniqueViolation:
    msg = strings["word_already_defined"]
    bot.send_message(chat_id=chat_id, text=msg)



# Check if word exists, insert or update query count
def search_ari_word(update: Update, context: CallbackContext):
  chat_id, _, _ = utils.update_get_ids(update)
  bot: Bot = context.bot

  # No argument?
  if (len(context.args) == 0):
    update.message.reply_text(strings["command_sana_no_word"])
    return

  word = context.args[0].lower()

  result = db.search_ari_word(word)

  msg = ""

  if len(result) == 0:
    msg = strings["no_words_found"]
    # TODO inline keyboard
  elif (result[0][0] == word):
    msg_end = strings["found_word_match_dictionary"] if result[0][1] else strings["found_word_match_not_dictionary"]
    msg = "{} {}".format(strings["found_word_match"], msg_end)
    # TODO increment query counter
  else:
    msg_end = ""
    for row in result:
      dictionary_string = strings["is_dictionary"] if row[1] else strings["is_not_dictionary"]
      msg_end += "\n{}, {}, {}: {}".format(row[0], dictionary_string, strings["likeness"], row[2])

    msg = "{} {}".format(strings["found_words"], msg_end)

  bot.send_message(chat_id=chat_id, text=msg)


# -----------------------------------------------------------------------------

def handlers(updater):
  dp = updater.dispatcher

  dp.add_handler(CommandHandler("start", start))
  dp.add_handler(CommandHandler("sana", search_ari_word))
  dp.add_handler(CommandHandler("lisaasana", add_ari_word))

def main():
  updater = Updater(tg_token, use_context=True)
  handlers(updater)

  updater.start_polling(poll_interval=2.0)

tg_token = environ["TG_TOKEN"]

db = DatabasePsql()

main()