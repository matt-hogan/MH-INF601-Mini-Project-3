DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS todo;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  first_name TEXT NOT NULL,
  last_name TEXT NOT NULL,
  email TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE todo (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  author_id INTEGER NOT NULL,
  title TEXT NOT NULL,
  description TEXT NOT NULL,
  completed INTEGER NOT NULL CHECK (completed IN (0, 1)),
  FOREIGN KEY (author_id) REFERENCES user (id)
);