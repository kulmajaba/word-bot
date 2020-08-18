# coding: utf-8

import csv
from datetime import date, datetime, timedelta
from os import environ
from typing import Union

import pytz
from pytz import timezone
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

import utils
from db_psql import DatabasePsql
from classes import LangCode, NewUser, QuestionState, VisitState
from strings import strings


new_users = {}


# -----------------------------------------------------------------------------

def get_lang_or_reply(chat_id: str, user_id: int, bot: Bot):
  lang = db.get_lang(user_id)

  if (lang is None):
    msg = "{}\n{}".format(strings[LangCode.FINNISH.value]["notregistered"], strings[LangCode.ENGLISH.value]["notregistered"])
    bot.send_message(chat_id=chat_id, text=msg)
  
  return lang


# -----------------------------------------------------------------------------

# Start registration flow
def start(update: Update, context: CallbackContext):
  chat_id, user_id, _ = utils.update_get_ids(update)
  bot: Bot = context.bot

  lang = db.get_lang(user_id)

  # User is already registered
  if (lang is not None):
    msg = "{}".format(strings[lang]["buttons"])
    bot.send_message(chat_id=chat_id, text=msg)
    return

  # User is not registered but has started the registration flow already
  if (user_id in new_users.keys()):
    state: QuestionState = new_users[user_id].current_question

    # User has answered language choice so we can ask the next question
    if (state != QuestionState.LANG):
      lang = new_users[user_id].lang

      msg = strings[lang][state.value]
      bot.send_message(chat_id=chat_id, text=msg)
      return
  # User has not started yet, start registration flow
  else:
    new_users[user_id] = NewUser()

  msg = "{}\n{}".format(strings[LangCode.FINNISH.value]["start"], strings[LangCode.ENGLISH.value]["start"])

  reply_markup: InlineKeyboardMarkup = InlineKeyboardMarkup([
    [InlineKeyboardButton("Finnish (fi)", callback_data=LangCode.FINNISH.value)],
    [InlineKeyboardButton("English (en)", callback_data=LangCode.ENGLISH.value)]
  ])

  bot.send_message(chat_id=chat_id, text=msg, reply_markup=reply_markup)

# Print help message
def help(update: Update, context: CallbackContext):
  chat_id, user_id, _ = utils.update_get_ids(update)
  bot: Bot = context.bot

  lang = db.get_lang(user_id)
  if (lang is not None):
    msg = strings[lang]["help"]

    if (user_id == tg_admin_id):
      msg += strings[lang]["adminmode"]
  else:
    msg = strings[LangCode.ENGLISH.value]["usestart"]

  bot.send_message(chat_id=chat_id, text=msg)

# Use custom keyboard for entering and exiting
def buttons(update: Update, context: CallbackContext):
  chat_id, user_id, _ = utils.update_get_ids(update)
  bot: Bot = context.bot

  lang = get_lang_or_reply(chat_id, user_id, bot)
  if (lang is None):
    return

  msg = strings[lang]["buttons"]

  reply_markup: InlineKeyboardMarkup = InlineKeyboardMarkup([
    [InlineKeyboardButton(strings[lang]["enter"], callback_data=VisitState.ENTER.value)],
    [InlineKeyboardButton(strings[lang]["exit"], callback_data=VisitState.EXIT.value)]
  ])

  bot.send_message(chat_id=chat_id, text=msg, reply_markup=reply_markup)

# New visit command
def visit_enter(update: Update, context: CallbackContext):
  chat_id, user_id, _ = utils.update_get_ids(update)
  bot: Bot = context.bot

  lang = get_lang_or_reply(chat_id, user_id, bot)
  if (lang is None):
    return

  timestamp: datetime = datetime.now(tz)

  print("Sign in user {} at time {}".format(user_id, timestamp.isoformat()))
  db.new_visit(user_id, timestamp.isoformat())

  msg = "{} {}".format(strings[lang]["latestenter"], utils.datetime_to_locale(timestamp))
  bot.send_message(chat_id=chat_id, text=msg)

# End visit command
def visit_exit(update: Update, context: CallbackContext):
  chat_id, user_id, _ = utils.update_get_ids(update)
  bot: Bot = context.bot

  lang = get_lang_or_reply(chat_id, user_id, bot)
  if (lang is None):
    return

  timestamp: datetime = datetime.now(tz)

  print("Sign out user {} at time {}".format(user_id, timestamp.isoformat()))
  db.end_visit(user_id, timestamp.isoformat())

  msg = "{} {}".format(strings[lang]["latestexit"], utils.datetime_to_locale(timestamp))
  bot.send_message(chat_id=chat_id, text=msg)

# Admin: get a CSV file of all visits in the database
def admin_get_report(update: Update, context: CallbackContext):
  chat_id, user_id, _ = utils.update_get_ids(update)
  bot: Bot = context.bot

  lang = get_lang_or_reply(chat_id, user_id, bot)
  if (lang is None):
    return
  
  if (user_id != tg_admin_id):
    msg = strings[lang]["noauth"]
    bot.send_message(chat_id=chat_id, text=msg)
    return
  
  data = db.admin_get_visits()

  filename = "{}-visits-{}.csv".format(organization.strip(' '), date.today().isoformat())

  print(data[0])

  with open(filename, 'w', newline='') as out:
    csv_out=csv.writer(out, dialect='excel', quotechar='|', escapechar='\\', quoting=csv.QUOTE_NONE)
    csv_out.writerow(['start time', 'end time', 'name', 'email'])
    csv_out.writerows(data)
    
    out.close()
  
  with open(filename, 'rb') as send:
    bot.send_document(chat_id=chat_id, document=send)
    send.close()


# -----------------------------------------------------------------------------
# User info

def get_user_info(update: Update, context: CallbackContext):
  chat_id, user_id, _ = utils.update_get_ids(update)
  bot: Bot = context.bot

  lang = get_lang_or_reply(chat_id, user_id, bot)
  if (lang is None):
    return
  
  data = db.get_user_info(user_id)

  msg = ""
  for d in data:
    msg += "{}\n".format(d)

  bot.send_message(chat_id=chat_id, text=msg)

def set_user_name(update: Update, context: CallbackContext):
  chat_id, user_id, _ = utils.update_get_ids(update)
  bot: Bot = context.bot

  lang = get_lang_or_reply(chat_id, user_id, bot)
  if (lang is None):
    return
  
  if (len(context.args) == 0):
    msg = strings[lang]["sthwrong"]
    bot.send_message(chat_id=chat_id, text=msg)
    return
  
  name = ' '.join(context.args)
  
  db.update_user(user_id, "name", name)

  msg = strings[lang]["infoupdated"]
  bot.send_message(chat_id=chat_id, text=msg)

def set_user_email(update: Update, context: CallbackContext):
  chat_id, user_id, _ = utils.update_get_ids(update)
  bot: Bot = context.bot

  lang = get_lang_or_reply(chat_id, user_id, bot)
  if (lang is None):
    return
  
  if (len(context.args) == 0):
    msg = strings[lang]["sthwrong"]
    bot.send_message(chat_id=chat_id, text=msg)
    return
  
  email = context.args[0]

  if (not utils.check_string_is_email(email)):
    msg = strings[lang]["sthwrong"]
    bot.send_message(chat_id=chat_id, text=msg)
    return
  
  db.update_user(user_id, "email", email)

  msg = strings[lang]["infoupdated"]
  bot.send_message(chat_id=chat_id, text=msg)


def set_user_lang(update: Update, context: CallbackContext):
  chat_id, user_id, _ = utils.update_get_ids(update)
  bot: Bot = context.bot

  lang = get_lang_or_reply(chat_id, user_id, bot)

  if (len(context.args) == 0):
    msg = strings[lang]["sthwrong"]
    bot.send_message(chat_id=chat_id, text=msg)
    return

  new_lang = context.args[0]

  if (new_lang not in [e.value for e in LangCode]):
    msg = strings[lang]["sthwrong"]
    bot.send_message(chat_id=chat_id, text=msg)
    return

  # Special case: someone still in registration flow uses the command
  if (lang is None):
    if (user_id in new_users.keys()):
      new_users[user_id].set_lang(new_lang)
      msg = strings[new_lang]["name"]
      bot.send_message(chat_id=chat_id, text=msg)
      return
  
  db.update_user(user_id, "lang", new_lang)

  msg = strings[new_lang]["infoupdated"]
  bot.send_message(chat_id=chat_id, text=msg)


# -----------------------------------------------------------------------------

# Inline keyboard callback, possible cases:
# Enter or exit buttons
# Registration flow language code select
def button_callback(update: Update, context: CallbackContext):
  chat_id, user_id, _ = utils.update_get_ids(update)
  bot: Bot = context.bot

  query: CallbackQuery = update.callback_query

  # CallbackQueries need to be answered, even if no notification to the user is needed
  # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
  query.answer()

  data = query.data

  # Callback is from enter or exit button
  if (data == VisitState.ENTER.value or data == VisitState.EXIT.value):
    chat_id, user_id, _ = utils.update_get_ids(update)
    bot: Bot = context.bot

    lang = get_lang_or_reply(chat_id, user_id, bot)
    if (lang is None):
      return

    timestamp: datetime = datetime.now(tz)
    msg = ""
    
    if (data == VisitState.ENTER.value):
      print("Sign in user {} at time {}".format(user_id, timestamp.isoformat()))
      db.new_visit(user_id, timestamp.isoformat())

      msg = "{}\n\n{} {}".format(strings[lang]["buttons"], strings[lang]["latestenter"], utils.datetime_to_locale(timestamp))
    else:
      print("Sign out user {} at time {}".format(user_id, timestamp.isoformat()))
      db.end_visit(user_id, timestamp.isoformat())

      msg = "{}\n\n{} {}".format(strings[lang]["buttons"], strings[lang]["latestexit"], utils.datetime_to_locale(timestamp))
    
    reply_markup: InlineKeyboardMarkup = InlineKeyboardMarkup([
      [InlineKeyboardButton(strings[lang]["enter"], callback_data=VisitState.ENTER.value)],
      [InlineKeyboardButton(strings[lang]["exit"], callback_data=VisitState.EXIT.value)]
    ])

    query.edit_message_text(text=msg, reply_markup=reply_markup)

    return

  if (user_id not in new_users.keys()):
    msg = "{} {}".format(strings[LangCode.ENGLISH.value]["sthwrong"], strings[LangCode.ENGLISH.value]["usestart"])
    bot.send_message(chat_id=chat_id, text=msg)
    return
  
  new_users[user_id].set_lang(data)

  msg = "{}\n\n{}".format(strings[LangCode.ENGLISH.value]["changelang"], strings[lang]["name"])

  query.edit_message_text(text=msg)

# Text message handler
# Is user is still in registration flow, they are inputting information
# Otherwise tell them to use buttons
def message(update: Update, context: CallbackContext):
  chat_id, user_id, _ = utils.update_get_ids(update)
  bot: Bot = context.bot

  lang = db.get_lang(user_id)

  # User is registered, ask to use buttons
  if (lang is not None):
    msg = "{}".format(strings[lang]["usebuttons"])
    bot.send_message(chat_id=chat_id, text=msg)
    return

  # User is not registered, ask to register
  if (user_id not in new_users.keys()):
    msg = "{}".format(strings[LangCode.ENGLISH.value]["usestart"])
    bot.send_message(chat_id=chat_id, text=msg)
    return
  
  # User is in registration flow, figure out what step they are at
  current_question: QuestionState = new_users[user_id].current_question
  
  # User hasn't selected the language yet
  if (current_question == QuestionState.LANG):
    msg = "{}".format(strings[LangCode.ENGLISH.value]["usebuttons"])
    bot.send_message(chat_id=chat_id, text=msg)
    return
  
  # User has selected the language, use it for the rest of the flow
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
  dp.add_handler(CommandHandler('enter', visit_enter))
  dp.add_handler(CommandHandler('sisaan', visit_enter))
  dp.add_handler(CommandHandler('exit', visit_exit))
  dp.add_handler(CommandHandler('ulos', visit_exit))
  dp.add_handler(CommandHandler('admin_get_report', admin_get_report))
  dp.add_handler(CommandHandler('getinfo', get_user_info))
  dp.add_handler(CommandHandler('setname', set_user_name))
  dp.add_handler(CommandHandler('setemail', set_user_email))
  dp.add_handler(CommandHandler('setlang', set_user_lang))
  dp.add_handler(CallbackQueryHandler(button_callback))
  dp.add_handler(MessageHandler(Filters.text, message))

def main():
  updater = Updater(tg_token, use_context=True)
  handlers(updater)

  updater.start_polling(poll_interval=2.0)


organization = environ["BOT_ORGANIZATION"]
tz = timezone(environ["PYTZ_TIMEZONE"])

tg_token = environ["TG_TOKEN"]
tg_admin_id = int(environ["TG_ADMIN_ID"])

db = DatabasePsql()

main()