import sys
from os import environ  

import psycopg2

from classes import LangCode, NewUser, QuestionState

class DatabasePsql:
  def __init__(self):
    self.db_name = environ["POSTGRES_DB"]
    self.db_user = environ["POSTGRES_USER"]
    self.db_pass = environ["POSTGRES_PASSWORD"]
    self.db_host = environ["POSTGRES_HOST"]
    self.db_port = environ["POSTGRES_PORT"]

    self.table_user = environ["POSTGRES_TABLE_USER"]
    self.table_visit = environ["POSTGRES_TABLE_VISIT"]

    self.fields_user = { # Boolean tells whether the value needs to be placed in quotes during update
      "name": True,
      "email": True,
      "lang": True
    }

  # Open new DB connection for operation
  def open_connection(self):
    conn = psycopg2.connect(
      dbname=self.db_name,
      user=self.db_user,
      password=self.db_pass,
      host=self.db_host,
      port=self.db_port
    )

    if conn.closed == 0:
      return conn
    else:
      return None
  
  # Insert new user
  # TODO: Does not check whether user exists
  def insert_user(self, user_id, new_user: NewUser):
    conn = self.open_connection()
    if conn == None:
      print('No DB connection')
      return
    
    cursor = conn.cursor()

    sql = "INSERT INTO {0} (user_id, name, email, lang) " \
          "VALUES ({1}, '{2}', '{3}', '{4}');"
    
    cursor.execute(sql.format(self.table_user, user_id, new_user.name, new_user.email, new_user.lang))

    conn.commit()
    conn.close()

  def get_user_info(self, user_id):
    conn = self.open_connection()
    if conn == None:
      print('No DB connection')
      return
    
    cursor = conn.cursor()

    sql = "SELECT name, email, lang FROM {0} " \
          "WHERE user_id = {1}"
    
    cursor.execute(sql.format(self.table_user, user_id))
    result = cursor.fetchone()

    conn.close()

    return result
  
  # Update user information
  # Field: One of visitor_user table fields
  def update_user(self, user_id, field, value):
    # Check if field name is valid
    if (field not in self.fields_user.keys()):
      print("update_user: given field name not valid")
      return

    conn = self.open_connection()
    if conn == None:
      print('No DB connection')
      return
    
    cursor = conn.cursor()

    # Add single quotes around the value if needed
    value_quotes = "'{}'".format(value) if self.fields_user[field] else value

    sql = "UPDATE {0} " \
          "SET {1} = {2} " \
          "WHERE user_id = {3};"
    
    cursor.execute(sql.format(self.table_user, field, value_quotes, user_id))

    conn.commit()
    conn.close()

  # Get user lang code
  # Can also be used to check if user exists
  def get_lang(self, user_id):
    conn = self.open_connection()
    if conn == None:
      print('No DB connection')
      return
        
    cursor = conn.cursor()

    sql = "SELECT lang FROM {0} " \
          "WHERE user_id = {1};"

    cursor.execute(sql.format(self.table_user, user_id))
    result = cursor.fetchone()
    
    conn.close()

    if (result is not None):
      result = result[0]

    return result
  
  # Compile all visits into CSV, sort by newest start time
  # Columns: start time, end time, name, email
  def admin_get_visits(self):
    conn = self.open_connection()
    if conn == None:
      print('No DB connection')
      return
        
    cursor = conn.cursor()

    sql = "SELECT start_time, end_time, name, email FROM {0} " \
          "INNER JOIN {1} ON {0}.user_id = {1}.user_id " \
          "ORDER BY start_time DESC;"

    cursor.execute(sql.format(self.table_visit, self.table_user))
    result = cursor.fetchall()

    conn.close()

    return result

  # Add new visit for user
  def new_visit(self, user_id, start_time):
    conn = self.open_connection()
    if conn == None:
      print('No DB connection')
      return
        
    cursor = conn.cursor()

    sql = "INSERT INTO {0} (user_id, start_time) " \
          "VALUES ({1}, '{2}');"

    cursor.execute(sql.format(self.table_visit, user_id, start_time))
    conn.commit()
    conn.close()
  
  # Add end time to the visit with the latest start time by the user
  def end_visit(self, user_id, end_time):
    conn = self.open_connection()
    if conn == None:
      print('No DB connection')
      return
        
    cursor = conn.cursor()

    sql = "UPDATE {0} " \
          "SET end_time = '{1}' " \
          "WHERE user_id = {2} AND start_time = (" \
            "SELECT max(start_time) FROM {0} WHERE user_id = {2}" \
          ");"

    cursor.execute(sql.format(self.table_visit, end_time, user_id))

    conn.commit()
    conn.close()

  def delete_old(self):
    conn = self.open_connection()
    if conn == None:
      print('No DB connection')
      return
        
    cursor = conn.cursor()

    sql = "DELETE FROM {0} " \
          "WHERE start_time < NOW() - INTERVAL '30 days';"

    cursor.execute(sql.format(self.table_visit))

    conn.commit()
    conn.close()

if __name__ == "__main__":
  asd = DatabasePsql()
