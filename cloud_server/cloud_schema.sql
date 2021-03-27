DROP TABLE IF EXISTS cloud;
DROP TABLE IF EXISTS events;


CREATE TABLE cloud (
  station TEXT NOT NULL,
  device TEXT NOT NULL,
  temp INTEGER NOT NULL,
  light_level INTEGER NOT NULL,
  time_recorded TIMESTAMP DEFAULT (datetime('now','localtime')) NOT NULL
);

CREATE table events (
  station TEXT NOT NULL,
  event_name TEXT NOT NULL,
  time_recorded TIMESTAMP DEFAULT (datetime('now','localtime')) NOT NULL
)