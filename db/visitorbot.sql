CREATE TYPE langcode AS ENUM ('fi', 'en');

CREATE TABLE IF NOT EXISTS visitor_user (
  user_id  BIGINT NOT NULL PRIMARY KEY,
  name     VARCHAR(255) NOT NULL,
  email    VARCHAR(255) NOT NULL,
  lang     langcode NOT NULL
);

CREATE TABLE IF NOT EXISTS visit (
  id          INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  user_id       BIGINT NOT NULL REFERENCES visitor_user(user_id),
  start_time  TIMESTAMP WITH TIME ZONE NOT NULL,
  end_time    TIMESTAMP WITH TIME ZONE
);