import sys
from os import environ  

import psycopg2

class DatabasePsql:
  def __init__(self):
    self.db_name = environ["POSTGRES_DB"]
    self.db_user = environ["POSTGRES_USER"]
    self.db_pass = environ["POSTGRES_PASSWORD"]
    self.db_host = environ["POSTGRES_HOST"]
    self.db_port = environ["POSTGRES_PORT"]

    self.table_ari_word = environ["POSTGRES_TABLE_WORD"]
    self.table_ari_word_query = environ["POSTGRES_TABLE_WORD_QUERY"]

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
  
  def search_ari_word(self, word):
    conn = self.open_connection()
    if conn == None:
      print('No DB connection')
      return
    
    cursor = conn.cursor()

    sql = "SELECT word, from_dictionary, SIMILARITY(word, '{0}') AS similarity FROM {1} " \
          "WHERE SIMILARITY(word, '{0}') > 0.4 " \
          "ORDER BY similarity DESC, word " \
          "LIMIT 3;"
    
    cursor.execute(sql.format(word, self.table_ari_word))
    result = cursor.fetchall()
    print(result)

    conn.close()

    return result
  
  # Insert new word
  def insert_ari_word(self, word, from_dictionary):
    conn = self.open_connection()
    if conn == None:
      print('No DB connection')
      return
    
    cursor = conn.cursor()

    sql = ""

    if not from_dictionary:
      sql = "INSERT INTO {0} (word, from_dictionary) " \
            "VALUES ('{1}', {2});"
    else:
      sql = "WITH word_insert AS (" \
            "INSERT INTO {0} (word, from_dictionary) " \
            "VALUES ('{1}', {2}) " \
            "RETURNING id" \
            ")" \
            "INSERT INTO {3} (ari_word_id) VALUES ((SELECT id FROM word_insert));"
    
    try:
      cursor.execute(sql.format(self.table_ari_word, word, from_dictionary, self.table_ari_word_query))

      conn.commit()
      conn.close()

      return True
    except psycopg2.errors.UniqueViolation as error:
      raise error

  # Get discovered dictionary words, total dictionary words and total original words
  def get_ari_word_stats(self):
    conn = self.open_connection()
    if conn == None:
      print('No DB connection')
      return
    
    cursor = conn.cursor()

    sql_count_found = "SELECT COUNT(id) FROM {0} " \
                      "INNER JOIN {1} ON {0}.id = {1}.ari_word_id" \
                      "WHERE from_dictionary = TRUE;"
    
    cursor.execute(sql_count_found.format(self.table_ari_word))
    result_found = cursor.fetchone()
    print(result_found)

    sql_count_unfound = "SELECT COUNT(id) FROM {0} " \
                        "WHERE from_dictionary = FALSE;"
    
    cursor.execute(sql_count_unfound.format(self.table_ari_word))
    result_unfound = cursor.fetchone()
    print(result_unfound)

    sql_count_unfound = "SELECT COUNT(id) FROM {0} " \
                        "WHERE from_dictionary = FALSE;"
    
    cursor.execute(sql_count_unfound.format(self.table_ari_word))
    result_unfound = cursor.fetchone()
    print(result_unfound)

    conn.close()

    return result
  
  # Update word query count
  def upsert_ari_word_query_count(self, word):
    conn = self.open_connection()
    if conn == None:
      print('No DB connection')
      return
    
    cursor = conn.cursor()

    sql = "INSERT INTO {0} (ari_word_id, query_count) " \
          "VALUES ((SELECT id FROM {1} WHERE word = {2}), 1) " \
          "ON CONFLICT ON CONSTRAINT ari_word_id " \
          "DO UPDATE SET query_count = query_count + 1"
    
    cursor.execute(sql.format(self.table_ari_word_query, self.table_ari_word, word))

    conn.commit()
    conn.close()

if __name__ == "__main__":
  asd = DatabasePsql()
