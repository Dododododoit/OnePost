CREATE TABLE users(
  username VARCHAR(20) NOT NULL,
  password VARCHAR(256) NOT NULL,
  PRIMARY KEY(username)
);

CREATE TABLE twitter(
  username VARCHAR(20) NOT NULL,
  accessToken VARCHAR(256) NOT NULL,
  accessTokenSecret VARCHAR(256) NOT NULL,
  PRIMARY KEY(username),
  FOREIGN KEY (username) REFERENCES users(username)
  ON DELETE CASCADE
);


CREATE TABLE instagram(
  username VARCHAR(20) NOT NULL,
  account VARCHAR(256) NOT NULL,
  password VARCHAR(256) NOT NULL,
  PRIMARY KEY(username),
  FOREIGN KEY (username) REFERENCES users(username)
  ON DELETE CASCADE
);

CREATE TABLE tumblr(
  username VARCHAR(20) NOT NULL,
  accessToken VARCHAR(256) NOT NULL,
  accessTokenSecret VARCHAR(256) NOT NULL,
  PRIMARY KEY(username),
  FOREIGN KEY (username) REFERENCES users(username)
  ON DELETE CASCADE
);