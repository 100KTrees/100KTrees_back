import psycopg2
from config import config
 
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
        part_name VARCHAR(255) NOT NULL
        )
        """,
        """ CREATE TABLE trees_history (
        tree_id INTEGER PRIMARY KEY,
        file_extension VARCHAR(5) NOT NULL,
        drawing_data BYTEA NOT NULL,
        FOREIGN KEY (tree_id)
        REFERENCES parts (part_id)
        ON UPDATE CASCADE ON DELETE CASCADE
        )
        """)
    conn = None
    try:
        # read the connection parameters
        params = config()
        # connect to the PostgreSQL server
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        # create table one by one
        for command in commands:
            cur.execute(command)
        # close communication with the PostgreSQL database server
        cur.close()
        # commit the changes
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
 
 
if __name__ == '__main__':
    create_tables()
