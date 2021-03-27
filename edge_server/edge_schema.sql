DROP TABLE IF EXISTS edge;

--implicit rowid
CREATE TABLE edge (
  device TEXT NOT NULL,
  temp INTEGER NOT NULL,
  light_level INTEGER NOT NULL,
  sent_to_cloud INTEGER DEFAULT 0 CHECK(sent_to_cloud = 0 or sent_to_cloud = 1) NOT NULL,
  time_recorded TIMESTAMP DEFAULT (datetime('now','localtime')) NOT NULL
);