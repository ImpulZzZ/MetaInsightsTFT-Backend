import mysql.connector

INITIALIZE_DATABASE_SQL = """
DROP DATABASE IF EXISTS TFT_META;
CREATE DATABASE TFT_META;

USE TFT_META;

-- Create the 'composition' table
CREATE TABLE composition (
    id INT AUTO_INCREMENT PRIMARY KEY,
    match_id VARCHAR(255) NOT NULL,
    level INT NOT NULL,
    placement INT NOT NULL,
    patch VARCHAR(20) NOT NULL,
    region VARCHAR(20) NOT NULL,
    match_time DATETIME NOT NULL
);

-- Create the 'champion' table with a foreign key reference to composition
CREATE TABLE champion (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    display_name VARCHAR(255) NOT NULL,
    tier INT NOT NULL,
    cost INT,
    icon VARCHAR(255) NOT NULL,
    composition_id INT,  -- Add a foreign key reference
    FOREIGN KEY (composition_id) REFERENCES composition(id)
);

-- Create the 'item' table
CREATE TABLE item (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    display_name VARCHAR(255) NOT NULL,
    not_component BOOLEAN DEFAULT 1,
    icon VARCHAR(255) NOT NULL,
    champion_id INT,
    FOREIGN KEY (champion_id) REFERENCES champion(id)
);

-- Create the 'trait' table
CREATE TABLE trait (
    name VARCHAR(255) NOT NULL,
    display_name VARCHAR(255) NOT NULL,
    style INT NOT NULL,
    tier_current INT NOT NULL,
    tier_total INT NOT NULL,
    icon VARCHAR(255) NOT NULL,
    composition_id INT,
    FOREIGN KEY (composition_id) REFERENCES composition(id)
);

-- Create the 'composition_group' table
CREATE TABLE composition_group (
    id INT AUTO_INCREMENT PRIMARY KEY,
    avg_placement DECIMAL(5, 2) NOT NULL,
    counter INT NOT NULL,
    grouped_by VARCHAR(255) NOT NULL
);

-- Create a new table for the many-to-many relationship between compositions and composition groups
CREATE TABLE composition_group_composition (
    composition_id INT NOT NULL,
    composition_group_id INT NOT NULL,
    FOREIGN KEY (composition_id) REFERENCES composition(id),
    FOREIGN KEY (composition_group_id) REFERENCES composition_group(id)
);
"""

def print_error_message(sql, error):
    print("Executing query failed!")
    print(f"SQL:   {sql}")
    print(f"Error: {error}")
    return None


## Creates and returns a connection to the database
def create_mysql_connection(host="localhost", user="root", password=None, database="TFT_META"):
    if password is None:  password = open("password.txt", "r").read()

    return mysql.connector.connect(host=host, user=user, password=password, database=database)


## TODO: Does not work
def initialize_empty_database():
    connection = create_mysql_connection(database="mysql")
    cursor = connection.cursor()
    try:
        cursor.execute(INITIALIZE_DATABASE_SQL, multi=True)
        connection.commit()
        return {"Success": "Database was successfully initialized!"}
    except Exception as err:
        return {"Error": f"Could not initialize database. Error: {err}"}
    finally:
        cursor.close()
        connection.close()


## Executes sql query and returns result as dictionary
def get_sql_data(sql, dictionary=True, multi=False):
    connection = create_mysql_connection()
    cursor = connection.cursor(dictionary=dictionary)
    try:
        cursor.execute(sql, multi=multi)
        data = cursor.fetchall()
        return data
    except mysql.connector.Error as err: print(f"Error: {err}")
    finally:
        cursor.close()
        connection.close()
    return None


## Executes sql query and returns result as dictionary
def get_match_by_id(id, dictionary=False):
    connection = create_mysql_connection()
    cursor = connection.cursor(dictionary=dictionary)
    try:
        cursor.execute(f"SELECT * FROM composition where match_id='{id}'")
        data = cursor.fetchall()
        return data
    except mysql.connector.Error as err: print(f"Error: {err}")
    finally:
        cursor.close()
        connection.close()
    return None


## Executes an insert query for a champion
def insert_champion(name, display_name, tier, cost, icon, composition_id):
    connection = create_mysql_connection()
    cursor = connection.cursor()
    escaped_display_name = display_name.replace("'", "\\\'")
    try:
        sql = f"INSERT INTO champion (name, display_name, tier, cost, icon, composition_id) VALUES ('{name}', '{escaped_display_name}', '{tier}', '{cost}', '{icon}', '{composition_id}')"
        cursor.execute(sql)
        connection.commit()
        last_inserted_id = cursor.lastrowid
        return last_inserted_id
    except mysql.connector.Error as err: print_error_message(sql, err)
    finally:
        cursor.close()
        connection.close()
    return None


## Executes an insert query for a item
def insert_item(name, display_name, icon, champion_id):
    connection = create_mysql_connection()
    cursor = connection.cursor()
    escaped_display_name = display_name.replace("'", "\\\'")
    try:
        sql = f"INSERT INTO item (name, display_name, icon, champion_id) VALUES ('{name}', '{escaped_display_name}', '{icon}', '{champion_id}')"
        cursor.execute(sql)
        connection.commit()
        last_inserted_id = cursor.lastrowid
        return last_inserted_id
    except mysql.connector.Error as err: print_error_message(sql, err)
    finally:
        cursor.close()
        connection.close()
    return None


## Executes an insert query for a trait
def insert_trait(name, display_name, style, tier_current, tier_total, icon, composition_id):
    connection = create_mysql_connection()
    cursor = connection.cursor()
    escaped_display_name = display_name.replace("'", "\\\'")
    try:
        sql = f"INSERT INTO trait (name, display_name, style, tier_current, tier_total, icon, composition_id) VALUES ('{name}', '{escaped_display_name}', '{style}', '{tier_current}', '{tier_total}', '{icon}', '{composition_id}')"
        cursor.execute(sql)
        connection.commit()
        last_inserted_id = cursor.lastrowid
        return last_inserted_id
    except mysql.connector.Error as err: print_error_message(sql, err)
    finally:
        cursor.close()
        connection.close()
    return None


## Executes an insert query for a composition
def insert_composition(match_id, level, placement, patch, region, match_time):
    connection = create_mysql_connection()
    cursor = connection.cursor()
    try:
        sql = f"INSERT INTO composition (match_id, level, placement, patch, region, match_time) VALUES ('{match_id}', '{level}', '{placement}', '{patch}', '{region}', '{match_time}')"
        cursor.execute(sql)
        connection.commit()
        last_inserted_id = cursor.lastrowid
        return last_inserted_id
    except mysql.connector.Error as err: print_error_message(sql, err)
    finally:
        cursor.close()
        connection.close()
    return None


## Executes an insert query for a composition_group
def insert_composition_group(avg_placement, counter, grouped_by):
    connection = create_mysql_connection()
    cursor = connection.cursor()
    try:
        sql = f"INSERT INTO composition_group (avg_placement, counter, grouped_by ) VALUES ('{avg_placement}', '{counter}', '{grouped_by}')"
        cursor.execute(sql)
        connection.commit()
        last_inserted_id = cursor.lastrowid
        return last_inserted_id
    except mysql.connector.Error as err: print_error_message(sql, err)
    finally:
        cursor.close()
        connection.close()
    return None


## Insert a new relationship entity between composition and composition group
def insert_composition_group_composition(composition_id, composition_group_id):
    connection = create_mysql_connection()
    cursor = connection.cursor()
    try:
        sql = f"INSERT INTO composition_group_composition (composition_id, composition_group_id ) VALUES ('{composition_id}', '{composition_group_id}')"
        cursor.execute(sql)
        connection.commit()
        last_inserted_id = cursor.lastrowid
        return last_inserted_id
    except mysql.connector.Error as err: print_error_message(sql, err)
    finally:
        cursor.close()
        connection.close()
    return None