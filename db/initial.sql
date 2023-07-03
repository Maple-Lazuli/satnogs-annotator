DROP DATABASE IF EXISTS inventory_db;    

CREATE DATABASE inventory_db; 

\c inventory_db;  

CREATE TABLE roles(
   role_id serial PRIMARY KEY,
   role_name VARCHAR (255) UNIQUE NOT NULL
);

CREATE TABLE accounts (
	account_id serial PRIMARY KEY,
	role_id INT NOT NULL,
	first_name VARCHAR ( 50 ) NOT NULL,
	last_name VARCHAR ( 50 ) NOT NULL,
	created_on TIMESTAMP NOT NULL,
	username VARCHAR ( 50 ) UNIQUE NOT NULL,
	password VARCHAR ( 128 ) NOT NULL,
	salt INT NOT NULL,
	locked BOOL NOT NULL,
	log_in_attempts INT NOT NULL,
  	FOREIGN KEY (role_id) REFERENCES roles (role_id)
	
);

CREATE TABLE permission_changes (
	change_id serial PRIMARY KEY,
	account_id INT NOT NULL,
	role_id INT NOT NULL,
	change_date TIMESTAMP NOT NULL,
	FOREIGN KEY (role_id) REFERENCES roles (role_id),
	FOREIGN KEY (account_id) REFERENCES accounts (account_id)
);

CREATE TABLE sessions (
	session_id serial PRIMARY KEY,
	account_id INT NOT NULL,
	creation_date TIMESTAMP NOT NULL,
	end_date TIMESTAMP NOT NULL,
	session_code VARCHAR ( 128 ),
	FOREIGN KEY (account_id) REFERENCES accounts (account_id)
);

CREATE TABLE items (
	item_id serial PRIMARY KEY,
	account_id INT NOT NULL,
	name VARCHAR ( 50 ) NULL,
	description VARCHAR ( 255 ) NULL,
	quantity INT NOT NULL,
	creation_date TIMESTAMP NOT NULL,
	modification_date TIMESTAMP,
	FOREIGN KEY (account_id) REFERENCES accounts (account_id)
);



