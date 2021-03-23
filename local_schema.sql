DROP TABLE IF EXISTS edge;

CREATE TABLE edge (
    temp INTEGER NOT NULL,
    light_level INTEGER NOT NULL,
    time_stamp TIMESTAMP DEFAULT (datetime('now', 'localtime')) NOT NULL
);


INSERT into edge (temp, light_level)
VALUES
  (34, 180)
;