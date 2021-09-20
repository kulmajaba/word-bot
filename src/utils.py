import re
from datetime import datetime
from os import environ

from telegram import TelegramError, Update, User
from telegram.ext import CommandHandler, Updater, CallbackContext


def update_get_ids(update: Update):
  """Return chat_id, user_id and message_id if they exist."""
  chat_id = update.effective_chat.id
  user_id = update.effective_user.id
  message_id = update.effective_message.message_id

  return chat_id, user_id, message_id
