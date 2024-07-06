import sqlite3

# Connect to the database (this will create it if it doesn't exist)
conn = sqlite3.connect('stock_market.db')
cursor = conn.cursor()

# SQLite script
sql_script = """
CREATE TABLE users (
  user_id INTEGER PRIMARY KEY ,
  full_name TEXT NOT NULL,
  nid_number TEXT NOT NULL UNIQUE CHECK(length(nid_number) = 12),
  phone_number TEXT NOT NULL UNIQUE CHECK(length(phone_number) = 11),
  password TEXT NOT NULL
);

CREATE TABLE wallets (
  wallet_id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL UNIQUE,
  balance REAL NOT NULL,
  FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE companies (
  company_id INTEGER PRIMARY KEY,
  company_name TEXT NOT NULL,
  sector TEXT NOT NULL,
  stock_price REAL NOT NULL
);

CREATE TABLE shares (
  share_id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL,
  company_id INTEGER NOT NULL,
  shares_owned INTEGER NOT NULL,
  FOREIGN KEY (user_id) REFERENCES users(user_id),
  FOREIGN KEY (company_id) REFERENCES companies(company_id)
);

-- Insert data for 5 users
INSERT INTO users (full_name, nid_number, phone_number, password)
VALUES
('ARNAB DAS', '123456789012', '01516592382', 'password1'),
('ZARIN TASNIM', '345678901234', '01789652383', 'password2'),
('UPOMA DEB', '567890123456', '01890562387', 'password3'),
('AFNAN MOHAMMED', '789012345678', '01756238966', 'password4'),
('AARON RAMSDALE', '890123456789', '01995566223', 'password5');

-- Insert balance data for 5 users
INSERT INTO wallets (user_id, balance)
VALUES
(1, 10000.00),
(2, 9500.00),
(3, 11000.00),
(4, 8500.00),
(5, 10250.00);

-- Add companies
INSERT INTO companies (company_name, sector, stock_price)
VALUES
  ('WALTON', 'Conglomerate', 100.00),
  ('Grameenphone Ltd', 'Telecom', 50.00),
  ('ACI Limited', 'Chemicals', 75.00),
  ('DUTCHBANGLA Bank', 'Banking', 45.00),
  ('LankaBangla Finance', 'Finance', 60.00);

-- Insert shares data
INSERT INTO shares (user_id, company_id, shares_owned)
VALUES 
(1, 1, 50),
(1, 2, 75),
(1, 4, 30),
(2, 2, 60),
(2, 3, 90),
(2, 5, 40),
(3, 1, 75),
(3, 4, 20),
(3, 5, 50),
(4, 3, 100),
(4, 5, 70),
(5, 1, 40),
(5, 2, 85),
(5, 3, 60);
"""

# Execute the SQL script
cursor.executescript(sql_script)

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Database created successfully.")