DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS movements;

CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  email TEXT,
  password TEXT NOT NULL
);

INSERT INTO users (id, username, email, password) VALUES (
  1, 
  "admin",
  NULL,
  --the password of admin
  "scrypt:32768:8:1$yMN6lSccevfnk3in$27c9fd47720cd6208e7d40d536e25346e6baa07cfb87525c4e7ac879b0afcad3dbe7e1aa78c69c0f1afed1ffac4faf94644cc23e7335a6f3aeb10a7ddeb57d3f"
);

CREATE TABLE products (
    product_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name         TEXT    NOT NULL,
    price        REAL    NOT NULL,
    quantity     INTEGER    NOT NULL,
    description  TEXT,
    created_by   INTEGER NOT NULL,
    FOREIGN KEY (created_by) REFERENCES users(id)
);

CREATE TABLE movements (
    id            INTEGER    PRIMARY KEY AUTOINCREMENT,
    user_id       INTEGER    NOT NULL,
    product_id    INTEGER    NOT NULL,
    type          TEXT       NOT NULL  CHECK(type IN ('in', 'out')),
    quantity      INTEGER    NOT NULL  DEFAULT 1,
    added_at      TIMESTAMP  NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);
