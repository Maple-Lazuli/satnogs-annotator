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

CREATE TABLE observations (
	observation_id serial PRIMARY KEY,
	satnogs_id INT UNIQUE NOT NULL,
	satellite_name VARCHAR ( 200 ) NOT NULL,
	station_name VARCHAR ( 200 ) NOT NULL,
	status VARCHAR ( 20 ) NOT NULL,
	status_code INT NOT NULL,
	transmitter VARCHAR ( 200 ) NOT NULL,
	frequency INT NOT NULL,
	pull_date TIMESTAMP NOT NULL,
	original_waterfall BYTEA NOT NULL,
	greyscaled_waterfall BYTEA NOT NULL,
	thresholded_waterfall BYTEA NOT NULL,
	waterfall_length INT NOT NULL,
	waterfall_width INT NOT NULL
);

CREATE TABLE annotations (
	annotation_id serial PRIMARY KEY,
	account_id INT NOT NULL,
	observation_id INT NOT NULL,
	creation_date TIMESTAMP NOT NULL,
	x0 FLOAT NOT NULL,
	y0 FLOAT NOT NULL,
	x1 FLOAT NOT NULL,
	y1 FLOAT NOT NULL,
	annotation_width FLOAT NOT NULL,
	annotation_height FLOAT NOT NULL,
	image_width FLOAT NOT NULL,
	image_height FLOAT NOT NULL,
	FOREIGN KEY (account_id) REFERENCES accounts (account_id),
	FOREIGN KEY (observation_id) REFERENCES observations (observation_id)
);

CREATE TABLE tasks (
	task_id serial PRIMARY KEY,
	observation_id INT NOT NULL,
	status VARCHAR ( 20 ) NOT NULL,
	start_date TIMESTAMP NOT NULL,
	completion_date TIMESTAMP,
	FOREIGN KEY (observation_id) REFERENCES observations (observation_id)
);


