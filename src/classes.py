from enum import Enum
from typing import Union

class QuestionState(Enum):
  LANG = "lang"
  NAME = "name"
  EMAIL = "email"
  DONE = "done"

class LangCode(Enum):
  FINNISH = "fi"
  ENGLISH = "en"

class NewUser:
  current_question: QuestionState = QuestionState.LANG
  lang: Union[LangCode, None] = None
  name: Union[str, None] = None
  email: Union[str, None] = None

  def set_lang(self, lang: LangCode):
    self.lang = lang
    self.current_question = QuestionState.NAME
  
  def set_name(self, name: str):
    self.name = name
    self.current_question = QuestionState.EMAIL
  
  def set_email(self, email: str):
    self.email = email
    self.current_question = QuestionState.DONE