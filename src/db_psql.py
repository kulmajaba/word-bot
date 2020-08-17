import sys
from os import environ  
import psycopg2

from classes import NewUser, QuestionState, LangCode

class DatabasePsql:
  def open_connection(self):
    db_name = environ["POSTGRES_DB"]
    db_user = environ["POSTGRES_USER"]
    db_pass = environ["POSTGRES_PASSWORD"]
    db_host = environ["POSTGRES_HOST"]
    db_port = environ["POSTGRES_PORT"]

    self.table_user = environ["POSTGRES_TABLE_USER"]
    self.table_visit = environ["POSTGRES_TABLE_VISIT"]
    self.fields_user = { # Boolean tells whether the value needs to be placed in quotes during update
      "user_id": False,
      "name": True,
      "email": True,
      "lang": True
    }

    conn = psycopg2.connect(
      dbname=db_name,
      user=db_user,
      password=db_pass,
      host=db_host,
      port=db_port
    )

    if conn.closed == 0:
      return conn
    else:
      return False
  
  def insert_user(self, user_id, new_user: NewUser):
    conn = self.open_connection()
    if conn == False:
      return
    
    cursor = conn.cursor()

    sql = "INSERT INTO {0} (user_id, name, email, lang) " \
          "VALUES ({1}, '{2}', '{3}', '{4}');"
    
    cursor.execute(sql.format(self.table_user, user_id, new_user.name, new_user.email, new_user.lang))

    conn.commit()
    conn.close()
  
  def update_user(self, user_id, field, value):
    if (field not in self.fields_user.keys()):
      print("Apua olen tyhmä paksukainen")
      return

    conn = self.open_connection()
    if conn == False:
      return
    
    cursor = conn.cursor()

    value_quotes = value if self.fields_user[field] else '{}'.format(value)

    sql = "UPDATE {0} " \
          "SET {1} = {2} " \
          "WHERE user_id = {3}];"
    
    cursor.execute(sql.format(self.table_user, field, value_quotes, user_id))

    conn.commit()
    conn.close()

  def get_lang(self, user_id):
    conn = self.open_connection()
    if conn == False:
      return
        
    cursor = conn.cursor()

    sql = "SELECT lang FROM {0} " \
          "WHERE user_id = {1};"

    cursor.execute(sql.format(self.table_user, user_id))
    result = cursor.fetchone()[0]
    conn.close()

    return result
      
  def new_visit(self, user_id, start_time):
    conn = self.open_connection()
    if conn == False:
      return
        
    cursor = conn.cursor()

    sql = "INSERT INTO {0} (user_id, start_time) " \
          "VALUES ({1}, '{2}');"

    cursor.execute(sql.format(self.table_visit, user_id, start_time))
    conn.commit()
    conn.close()
  
  def end_visit(self, user_id, end_time):
    conn = self.open_connection()
    if conn == False:
      return
        
    cursor = conn.cursor()

    sql = "UPDATE {0} " \
          "SET end_time = '{1}' " \
          "WHERE user_id = {2} AND start_time = (SELECT max(start_time) FROM {0} WHERE user_id = {2});"

    cursor.execute(sql.format(self.table_visit, end_time, user_id))
    conn.commit()
    conn.close()


if __name__ == "__main__":
  asd = DatabasePsql()
