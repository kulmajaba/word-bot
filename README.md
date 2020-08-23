# Visitorbot

Telegram bot for recording visitors to a space.
* Easy usage through Telegram: register with your name and email, after that use the buttons to sign yourself in or out.
  - ![Demo 1](https://i.imgur.com/u59mYKo.gif)
* Deletes records older that 30 days automatically
* Allows a single admin user to get a CSV file containing all visits from the past 30 days via Telegram.
  - ![Demo 2](https://i.imgur.com/BHSQa8P.gif)

## Setup

The backend is built using Docker and docker-compose, but should be possible to run without Docker as well. The implementation is done with Python 3.8.5 using PostgreSQL 12

Copy or rename the `.env.sample` file to the same folder as `.env` and fill in the missing information.

| Variable          | Description |
| ----------------- | ----------- |
| BOT_ORGANIZATION  | The name of the organization the bot belongs to, currently only used for report file names. |
| PYTZ_TIMEZONE     | Timezone used by Python, use valid Pytz timezones. E.g. Europe/Helsinki. You'll probably want to match the database timezones. |
| TZ                | Postgres timezone. |
| PGTZ              | Postgres default timezone. |
| TG_TOKEN          | Telegram API token for the bot. |
| TG_ADMIN_ID       | Telegram user ID (not username) of the admin, enables the ability to fetch reports. Use e.g. [@userinfobot](https://t.me/userinfobot) to get your ID. |
| POSTGRES_DB       | Postgres database name. Used by both PostgreSQL and Python code. |
| POSTGRES_USER     | Postgres user for DB access. Same as above. |
| POSTGRES_PASSWORD | Postgres user password. Same as above. |
| POSTGRES_HOST     | Hostname for the Python code to use when connecting to the DB, use `db` for Docker installations with the default docker-compose file |
| POSTGRES_PORT     | Postgres port, used by both PostgreSQL and Python code. |
| POSTGRES_TABLE_USER | Table name for the users of the bot, use `visitor_user` for installations with the default database initialization |
| POSTGRES_TABLE_VISIT | Table name for the visits, use `visit` for installations with the default database initialization |

After that, you should be able to build and run the bot with `docker-compose up -d`. Add `--build` to rebuild images and/or `--force-recreate` to recreate the application containers.

Check logs with `docker-compose logs`, `-f` to follow, shut down with `docker-compose down`.
