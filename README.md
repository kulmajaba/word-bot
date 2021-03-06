# Wordbot

Telegram-bot for words around a specific topic.

## Setup

To parse dictionary words, download kotus-sanalista_v1 and run `WORD=asd python db/parse-kotus.py` from the project root. This will create the file `init_words.sql` which is required to initialize the DB.

The backend is built using Docker and docker-compose, but should be possible to run without Docker as well. The implementation is done with Python 3.8.5 using PostgreSQL 12

Copy or rename the `.env.sample` file to the same folder as `.env` and fill in the missing information.

| Variable          | Description |
| ----------------- | ----------- |
| TG_TOKEN          | Telegram API token for the bot. |
| LOCALE            | Language, e.q. `fi`. Ensure the locale translations exist in `strings.py`. |
| WORD              | The substring to search for. |
| PGTZ              | Postgres default timezone. |
| POSTGRES_DB       | Postgres database name. Used by both PostgreSQL and Python code. |
| POSTGRES_USER     | Postgres user for DB access. Same as above. |
| POSTGRES_PASSWORD | Postgres user password. Same as above. |
| POSTGRES_HOST     | Hostname for the Python code to use when connecting to the DB, use `db` for Docker installations with the default docker-compose file |
| POSTGRES_PORT     | Postgres port, used by both PostgreSQL and Python code. |
| POSTGRES_TABLE_WORD | Table name for the words, use `word` for installations with the default database initialization |
| POSTGRES_TABLE_WORD_QUERY | Table name for word query counts, use `word_query` for installations with the default database initialization |

After that, you should be able to build and run the bot with `docker-compose up -d`. Add `--build` to rebuild images and/or `--force-recreate` to recreate the application containers.

Check logs with `docker-compose logs`, `-f` to follow, shut down with `docker-compose down`.
