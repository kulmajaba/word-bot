import re
from datetime import datetime
from os import environ

from pytz import timezone
from telegram import TelegramError, Update, User
from telegram.ext import CommandHandler, Updater, CallbackContext

tz = timezone(environ["PYTZ_TIMEZONE"])

def update_get_ids(update: Update):
  """Return chat_id, user_id and message_id if they exist."""
  chat_id = update.effective_chat.id
  user_id = update.effective_user.id
  message_id = update.effective_message.message_id

  return chat_id, user_id, message_id

def check_string_is_email(email: str):
  regex = '^.+@.+$'

  if (not re.search(regex, email)):
    return False
  
  return True

def check_update_is_email(update: Update):
  email = update.effective_message.text
  
  return check_string_is_email(email)

def datetime_to_locale(dt: datetime):
  fmt = '%Y-%m-%d %H:%M:%S %Z'

  dt_loc = dt.astimezone(tz)
  return dt_loc.strftime(fmt)
