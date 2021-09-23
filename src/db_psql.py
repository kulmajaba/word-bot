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

    self.table_word = environ["POSTGRES_TABLE_WORD"]
    self.table_word_query = environ["POSTGRES_TABLE_WORD_QUERY"]

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
  
  def search_word(self, word):
    """Search for a word

    Args:
        word (String)

    Returns:
        List<Tuple>: (word, from_dictionary, likeness)
    """
    conn = self.open_connection()
    if conn == None:
      print('No DB connection')
      return
    
    cursor = conn.cursor()

    sql = "SELECT word, from_dictionary, SIMILARITY(word, '{0}') AS similarity FROM {1} " \
          "WHERE SIMILARITY(word, '{0}') > 0.4 " \
          "ORDER BY similarity DESC, word " \
          "LIMIT 3;"
    
    cursor.execute(sql.format(word, self.table_word))
    result = cursor.fetchall()
    print(result)

    conn.close()

    return result
  
  def insert_word(self, word, from_dictionary):
    """Insert a new word

    Args:
        word (String)
        from_dictionary (Boolean): Sets whether the word is from a dictionary or original

    Raises:
        error: psycopg2.errors.UniqueViolation if the word is already in the database
    """
    conn = self.open_connection()
    if conn == None:
      print('No DB connection')
      return
    
    cursor = conn.cursor()

    sql = ""

    if from_dictionary:
      sql = "INSERT INTO {0} (word, from_dictionary) " \
            "VALUES ('{1}', {2});"
    else:
      sql = "WITH word_insert AS (" \
            "INSERT INTO {0} (word, from_dictionary) " \
            "VALUES ('{1}', {2}) " \
            "RETURNING id" \
            ") " \
            "INSERT INTO {3} (word_id) VALUES ((SELECT id FROM word_insert));"
    
    try:
      cursor.execute(sql.format(self.table_word, word, from_dictionary, self.table_word_query))

      conn.commit()
      conn.close()

    except psycopg2.errors.UniqueViolation as error:
      self.increment_word_query_count(word)
      raise error
  
  def increment_word_query_count(self, word):
    """Update word query count

    Args:
        word (String)

    Returns:
      Query count for the word
    """
    conn = self.open_connection()
    if conn == None:
      print('No DB connection')
      return
    
    cursor = conn.cursor()

    sql = "INSERT INTO {0} (word_id) " \
          "VALUES ((SELECT id FROM {1} WHERE word = '{2}')) " \
          "ON CONFLICT (word_id) " \
          "DO UPDATE SET query_count = {0}.query_count + 1 " \
          "RETURNING query_count;"
    
    cursor.execute(sql.format(self.table_word_query, self.table_word, word))

    result = cursor.fetchone()[0]

    conn.commit()
    conn.close()

    return result

  def get_stats(self):
    """Get stats about the discovered and undiscovered words

    Returns:
      Tuple(words discovered from dictionary, total words in dictionary, words added not in dictionary)
    """
    conn = self.open_connection()
    if conn == None:
      print('No DB connection')
      return
    
    cursor = conn.cursor()

    sql_count_found = "SELECT " \
                      "COUNT({0}.id) FILTER (WHERE from_dictionary = TRUE AND query_count IS NOT NULL) as dict_found_count, " \
                      "COUNT({0}.id) FILTER (WHERE from_dictionary = TRUE) as dict_total_count, " \
                      "COUNT({0}.id) FILTER (WHERE from_dictionary = FALSE) as non_dict_count " \
                      "FROM {0} " \
                      "LEFT JOIN {1} ON {0}.id = {1}.word_id;"
    
    cursor.execute(sql_count_found.format(self.table_word, self.table_word_query))
    result = cursor.fetchone()

    conn.close()

    return result
  
  def get_top_words(self):
    """Get top searched for words

    Returns:
      List<Tuple>: (word, from_dictionary, count)
    """
    conn = self.open_connection()
    if conn == None:
      print('No DB connection')
      return
    
    cursor = conn.cursor()

    sql_count_found = "SELECT word, from_dictionary, query_count " \
                      "FROM {0} " \
                      "INNER JOIN {1} ON {0}.id = {1}.word_id " \
                      "ORDER BY query_count DESC, word ASC " \
                      "LIMIT 10;"
    
    cursor.execute(sql_count_found.format(self.table_word, self.table_word_query))
    result = cursor.fetchall()

    conn.close()

    return result

if __name__ == "__main__":
  asd = DatabasePsql()
