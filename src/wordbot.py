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

  msg = "{}".format(strings[LOCALE]["start"].format(BOT_WORD.capitalize()))
  bot.send_message(chat_id=chat_id, text=msg)

def add_word(update: Update, context: CallbackContext):
  chat_id, user_id, _ = utils.update_get_ids(update)
  bot: Bot = context.bot

  # No argument?
  if (len(context.args) == 0):
    update.message.reply_text(strings[LOCALE]["command_sana_no_word"])
    return

  word = context.args[0].lower()

  if (BOT_WORD not in word):
    update.message.reply_text(strings[LOCALE]["no_substring_in_word"].format(BOT_WORD))
    return

  try:
    result = db.insert_word(word, False)
    msg = strings[LOCALE]["word_added"]
    bot.send_message(chat_id=chat_id, text=msg)
  except psycopg2.errors.UniqueViolation:
    msg = strings[LOCALE]["word_already_defined"]
    bot.send_message(chat_id=chat_id, text=msg)

# Check if word exists, insert or update query count
def search_word(update: Update, context: CallbackContext):
  chat_id, _, _ = utils.update_get_ids(update)
  bot: Bot = context.bot

  # No argument?
  if (len(context.args) == 0):
    update.message.reply_text(strings[LOCALE]["command_sana_no_word"])
    return

  word = context.args[0].lower()

  if (BOT_WORD not in word):
    update.message.reply_text(strings[LOCALE]["no_substring_in_word"].format(BOT_WORD))
    return

  result = db.search_word(word)

  msg = ""

  if len(result) == 0:
    msg = strings[LOCALE]["no_words_found"]
  elif (result[0][0] == word):
    msg_end = strings[LOCALE]["found_word_match_dictionary"] if result[0][1] else strings[LOCALE]["found_word_match_not_dictionary"]
    msg = "{} {}".format(strings[LOCALE]["found_word_match"], msg_end)

    count = db.increment_word_query_count(word)
    msg += " {}".format(strings[LOCALE]["word_query_count"].format(count))
  else:
    msg_end = ""
    for row in result:
      dictionary_string = strings[LOCALE]["is_dictionary"] if row[1] else strings[LOCALE]["is_not_dictionary"]
      msg_end += "\n{}, {}, {}: {}".format(row[0], dictionary_string, strings[LOCALE]["likeness"], row[2])

    msg = "{} {}".format(strings[LOCALE]["found_words"], msg_end)

  bot.send_message(chat_id=chat_id, text=msg)

# Get stats
def stats(update: Update, context: CallbackContext):
  chat_id, _, _ = utils.update_get_ids(update)
  bot: Bot = context.bot

  result = db.get_stats()

  top_10 = db.get_top_words()

  msg = strings[LOCALE]["stats"].format(result[0], result[1], result[2])
  msg += "\n\n{}".format(strings[LOCALE]["top_list"].format(len(top_10)))

  for i, row in enumerate(top_10):
    dictionary_string = strings[LOCALE]["is_dictionary"] if row[1] else strings[LOCALE]["is_not_dictionary"]
    count_string = strings[LOCALE]["word_query_count"].format(row[2])
    msg += "\n{}. {}, {}, {}".format(i + 1, row[0], dictionary_string, count_string)
  
  bot.send_message(chat_id=chat_id, text=msg)
  


# -----------------------------------------------------------------------------

def handlers(updater):
  dp = updater.dispatcher

  dp.add_handler(CommandHandler("start", start))
  dp.add_handler(CommandHandler("sana", search_word))
  dp.add_handler(CommandHandler("word", search_word))
  dp.add_handler(CommandHandler("lisaasana", add_word))
  dp.add_handler(CommandHandler("addword", add_word))
  dp.add_handler(CommandHandler("stats", stats))

def main():
  updater = Updater(TG_TOKEN, use_context=True)
  handlers(updater)

  updater.start_polling(poll_interval=2.0)

TG_TOKEN = environ["TG_TOKEN"]
LOCALE = environ["LOCALE"]
BOT_WORD = environ["WORD"]

db = DatabasePsql()

main()