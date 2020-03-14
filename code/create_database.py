import psycopg2
import json


def load_configs():
    # TODO: set correct config file path
    config_file = "../config/config.json"
    with open(config_file, "r+") as config:
        data = json.load(config)
    return data
 
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
        tree_broken BOOLEAN NOT NULL,
        
        )
        """,
        """ CREATE TABLE users (
        user_id SERIAL PRIMARY KEY,
        user_email VARCHAR(255) NOT NULL,
        user_password VARCHAR(255) NOT NULL,
        user_city VARCHAR(255) NOT NULL,
        user_state VARCHAR(255) NOT NULL,
        user_country VARCHAR(255) NOT NULL,
        user_zip VARCHAR9(255) NOT NULL,
        user_date_created DATETIME NOT NULL
        user_photo_html VARCHAR(255) NOT NULL,
        )
        """,
        """ CREATE TABLE trees_history (
        tree_id SERIAL PRIMARY KEY,
        user_id SERIAL PRIMARY KEY,
        tree_history_action DATETIME NOT NULL, 
        tree_history_date DATETIME NOT NULL, 
        FOREIGN KEY (tree_id, user_id)
        ON UPDATE CASCADE ON DELETE CASCADE
        )
        """)
    conn = None
    try:
        params = load_configs()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        for command in commands:
            cur.execute(command)
        cur.close()
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
 
 
if __name__ == '__main__':
    create_tables()