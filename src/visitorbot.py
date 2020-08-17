# coding: utf-8

from datetime import datetime, timedelta, timezone
from os import environ
from typing import Union

from telegram import TelegramError, Update, Bot, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import CommandHandler, Updater, CallbackContext, CallbackQueryHandler, MessageHandler, Filters

from db_psql import DatabasePsql
from strings import strings
import utils
from classes import NewUser, QuestionState, LangCode


new_users = {}


# -----------------------------------------------------------------------------


def start(update: Update, context: CallbackContext):
  chat_id, user_id, _ = utils.update_get_ids(update)
  bot: Bot = context.bot

  lang = db.get_lang(user_id)

  if (lang is not None):
    msg = "{}".format(strings[lang]["buttons"])
    bot.send_message(chat_id=chat_id, text=msg)
    return

  if (user_id in new_users.keys()):
    state: QuestionState = new_users[user_id].current_question

    if (state != QuestionState.LANG):
      lang = new_users[user_id].lang

      msg = strings[lang][state.value]
      bot.send_message(chat_id=chat_id, text=msg)
      return
  else:
    new_users[user_id] = NewUser()

  msg = "{}\n{}".format(strings[LangCode.FINNISH.value]["start"], strings[LangCode.ENGLISH.value]["start"])

  reply_markup: InlineKeyboardMarkup = InlineKeyboardMarkup([
    [InlineKeyboardButton("Finnish (fi)", callback_data=LangCode.FINNISH.value)],
    [InlineKeyboardButton("English (en)", callback_data=LangCode.ENGLISH.value)]
  ])

  bot.send_message(chat_id=chat_id, text=msg, reply_markup=reply_markup)

def help(update: Update, context: CallbackContext):
  chat_id, _, msg_id = utils.update_get_ids(update)
  bot: Bot = context.bot

  bot.send_sticker(chat_id, utils.helpSticker, reply_to_message_id=msg_id)

def buttons(update: Update, context: CallbackContext):
  chat_id, user_id, _ = utils.update_get_ids(update)
  bot: Bot = context.bot

  lang = db.get_lang(user_id)

  kb = ReplyKeyboardMarkup(
    [
      [KeyboardButton(strings[lang]["in"])],
      [KeyboardButton(strings[lang]["out"])]
    ],
    resize_keyboard=True
  )

  msg = strings[lang]["buttons"]
  bot.send_message(chat_id=chat_id, text=msg, reply_markup=kb)

def button(update: Update, context: CallbackContext):
  chat_id, user_id, _ = utils.update_get_ids(update)
  bot: Bot = context.bot

  query: CallbackQuery = update.callback_query

  # CallbackQueries need to be answered, even if no notification to the user is needed
  # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
  query.answer()

  if (user_id not in new_users.keys()):
    msg = "{} {}".format(strings[LangCode.ENGLISH.value]["sthwrong"], strings[LangCode.ENGLISH.value]["usestart"])
    bot.send_message(chat_id=chat_id, text=msg)
    return

  lang = query.data
  
  new_users[user_id].set_lang(lang)

  msg = "{}\n\n{}".format(strings[LangCode.ENGLISH.value]["changelang"], strings[lang]["name"])

  query.edit_message_text(text=msg)

def message(update: Update, context: CallbackContext):
  chat_id, user_id, _ = utils.update_get_ids(update)
  bot: Bot = context.bot

  lang = db.get_lang(user_id)

  if (lang is not None):
    text = update.message.text

    if (text == strings[LangCode.ENGLISH.value]["in"] or text == strings[LangCode.FINNISH.value]["in"]):
      timestamp: datetime = datetime.now(timezone.utc)
      
      print("Sign in user {} at time {}".format(user_id, timestamp.isoformat()))
      db.new_visit(user_id, timestamp.isoformat())
      return
    elif (text == strings[LangCode.ENGLISH.value]["out"] or text == strings[LangCode.FINNISH.value]["out"]):
      timestamp: datetime = datetime.now(timezone.utc)

      print("Sign out user {} at time {}".format(user_id, timestamp.isoformat()))
      db.end_visit(user_id, timestamp.isoformat())
      return
    else:
      msg = "{}".format(strings[lang]["buttons"])
      bot.send_message(chat_id=chat_id, text=msg)
      return

  if (user_id not in new_users.keys()):
    msg = "{}".format(strings[LangCode.ENGLISH.value]["usestart"])
    bot.send_message(chat_id=chat_id, text=msg)
    return
  
  current_question: QuestionState = new_users[user_id].current_question
  
  if (current_question == QuestionState.LANG):
    msg = "{}".format(strings[LangCode.ENGLISH.value]["usebuttons"])
    bot.send_message(chat_id=chat_id, text=msg)
    return
  
  lang = new_users[user_id].lang

  if (current_question == QuestionState.NAME):
    name = ""

    try:
      name = update.message.text
    except:
      msg = "{} {}".format(strings[lang]["sthwrong"], strings[lang]["name"])
      bot.send_message(chat_id=chat_id, text=msg)
      return

    new_users[user_id].set_name(name)

    msg = strings[lang]["email"]
    bot.send_message(chat_id=chat_id, text=msg)
    return
  elif (current_question == QuestionState.EMAIL):
    email = ""

    try:
      email = update.message.text
    except:
      msg = "{} {}".format(strings[lang]["sthwrong"], strings[lang]["email"])
      bot.send_message(chat_id=chat_id, text=msg)
      return

    if (not utils.check_update_is_email(update, context)):
      msg = "{} {}".format(strings[lang]["sthwrong"], strings[lang]["email"])
      bot.send_message(chat_id=chat_id, text=msg)
      return

    new_user = new_users[user_id]
    new_user.set_email(email)

    db.insert_user(user_id, new_user)

    del new_users[user_id]

    msg = strings[lang]["setupdone"]
    bot.send_message(chat_id=chat_id, text=msg)
    return


# -----------------------------------------------------------------------------


def handlers(updater):
  dp = updater.dispatcher

  dp.add_handler(CommandHandler('start', start))
  dp.add_handler(CommandHandler('help', help))
  dp.add_handler(CommandHandler('buttons', buttons))
  dp.add_handler(CommandHandler('napit', buttons))
  dp.add_handler(CallbackQueryHandler(button))
  dp.add_handler(MessageHandler(Filters.text, message))

def main():
  updater = Updater(tg_token, use_context=True)
  handlers(updater)

  updater.start_polling(poll_interval=2.0)


tg_token = environ["TG_TOKEN"]

db = DatabasePsql()

main()