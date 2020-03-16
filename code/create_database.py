import psycopg2 as ps
import pandas as pd
import json
#Note: A preexisting database called "100KTrees" is needed outside of this script"

def load_configs():
    # TODO: set correct config file path
    config_file = "../config/config.json"
    with open(config_file, "r+") as config:
        data = json.load(config)
    return data
def get_conn():
    params = load_configs()
    conn = ps.connect(
        dbname=params["dbname"], 
        user=params["user"],
        host = params["host"],
        password=params["password"]
        )
    return conn
def create_database():
    """after starting postgresql from command line, i used the following lines 
    to initialize the database as well as to create the user and the role
    for the user"""
    """
    CREATE DATABASE "100KTrees";
    CREATE USER user_name with encrypted password 'password';
    GRANT ALL PRIVILEGES ON DATABASE "100KTrees" TO user_name;

    ALTER USER user_name CREATEDB;
    """
def create_tables():
    """ create tables in the PostgreSQL database"""
    commands = (
        """CREATE TABLE trees (
        tree_id SERIAL PRIMARY KEY,
        tree_status BOOLEAN NOT NULL,
        tree_name VARCHAR(255) NOT NULL,
        tree_scientific_name VARCHAR(255) NOT NULL,  
        tree_longitude float8 NOT NULL,
        tree_latitude float8 NOT NULL,
        tree_street_address VARCHAR(255) NOT NULL,
        tree_city VARCHAR(255) NOT NULL,
        tree_state VARCHAR(255) NOT NULL,
        tree_country VARCHAR(255) NOT NULL,
        tree_zip VARCHAR(255) NOT NULL,
        tree_water_level float8 NOT NULL,
        tree_health INTEGER NOT NULL,
        tree_insects BOOLEAN NOT NULL,
        tree_broken BOOLEAN NOT NULL
        )
        """,
        """ CREATE TABLE users (
        user_id SERIAL PRIMARY KEY,
        user_email VARCHAR(255) NOT NULL,
        user_password VARCHAR(255) NOT NULL,
        user_city VARCHAR(255) NOT NULL,
        user_state VARCHAR(255) NOT NULL,
        user_country VARCHAR(255) NOT NULL,
        user_zip VARCHAR(255) NOT NULL,
        user_date_created TIMESTAMP default current_timestamp,
        user_photo_html VARCHAR(255) NOT NULL
        )
        """,
        """ CREATE TABLE trees_history (
        tree_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        tree_history_action VARCHAR(255) NOT NULL, 
        tree_history_date TIMESTAMP default current_timestamp,
        PRIMARY KEY (tree_id, user_id)
        )
        """)
    conn = None
    try:
        conn = get_conn()
        cur = conn.cursor()
        for command in commands:
            print(command)
            cur.execute(command)
        cur.close()
        conn.commit()
    except (Exception, ps.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
 
def load_sample_data():
    conn = get_conn()
    tree_data = pd.read_excel('../data/trees_schema.xlsx', sheetname='trees')
    user_data = pd.read_excel('../data/trees_schema.xlsx', sheetname='users')
    tree_history_data = pd.read_excel('../data/trees_schema.xlsx', sheetname='trees_history')
    #insert_rows
    #insert_cols
    #query

if __name__ == '__main__':
    create_tables()