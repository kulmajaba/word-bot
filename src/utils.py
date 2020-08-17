import re

from telegram import TelegramError, Update, User
from telegram.ext import CommandHandler, Updater, CallbackContext

helpSticker = "CAACAgQAAxkBAAEBNhJfOZ8EREBB_eOAMq_mX4jw6u7mYgACHwADkNFAA0p1bXFraxaPGgQ"

def printlog(update: Update, msg_type: str):
  username: User = update.effective_user

  print("Username: ", username,"\nType: ", msg_type)

  print()

def update_get_ids(update: Update):
  """Return chat_id, user_id and message_id if they exist."""
  chat_id = update.effective_chat.id
  user_id = update.effective_user.id
  message_id = update.effective_message.message_id

  return chat_id, user_id, message_id

def check_arg_is_string(update: Update, context: CallbackContext):
  chat_id, _, _ = update_get_ids(update)
  args = context.args
  bot = context.bot

  if (len(args) == 0):
    msg = "APUA"
    bot.send_message(chat_id=chat_id, text=msg)
    return False
  
  return True

def check_update_is_email(update: Update, context: CallbackContext):
  chat_id, _, _ = update_get_ids(update)
  email = update.effective_message.text
  bot = context.bot
  
  regex = '^.+@.+$'

  if (not re.search(regex, email)):
    msg = "APUA"
    bot.send_message(chat_id=chat_id, text=msg)
    return False
  
  return True
