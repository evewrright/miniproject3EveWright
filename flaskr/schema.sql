DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS appointment;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE student (
  id INTEGER PRIMARY KEY,
  first_name TEXT NOT NULL,
  last_name TEXT NOT NULL
);

CREATE TABLE appointment (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  author_id INTEGER NOT NULL,
  student_id INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  occurred DATE NOT NULL,
  topic TEXT NOT NULL,
  note TEXT NOT NULL,
  FOREIGN KEY (author_id) REFERENCES user (id),
  FOREIGN KEY (student_id) REFERENCES student (id)
);

INSERT INTO student (id, first_name, last_name) VALUES (786423, 'Zachary', 'Smith');
INSERT INTO student (id, first_name, last_name) VALUES (786639, 'Kaden', 'Bloom');
INSERT INTO student (id, first_name, last_name) VALUES (789622, 'Emily', 'Waltz');


