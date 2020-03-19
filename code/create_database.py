import psycopg2 as ps
import pandas as pd
import json
#Note: A preexisting database called "100KTrees" is needed outside of this script"

def load_configs():
    """
    load_configs: load the configs json
    inputs:
        None
    outputs:
        data - config json
    """

    config_file = "../config/config.json"
    with open(config_file, "r+") as config:
        data = json.load(config)
    return data
def get_conn():
    """
    get_conn: get the connection from postgres
    inputs: 
        None
    outputs:
        conn - connection object from postgres
    """
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
    for the user -- i am not sure how to do this programatically"""
    
    #CREATE DATABASE "100KTrees";
    #CREATE USER user_name with encrypted password 'password';
    #GRANT ALL PRIVILEGES ON DATABASE "100KTrees" TO user_name;

    #ALTER USER user_name CREATEDB;
    return

def create_tables():
    """
    create_tables: create tables in the PostgreSQL database
    inputs:
        None
    outputs:
        SQL - tables created in the database
    """
    commands = (
        "DROP TABLE IF EXISTS tree_inventory",
        "DROP TABLE IF EXISTS trees",
        "DROP TABLE IF EXISTS users",
        "DROP TABLE IF EXISTS users_log",
        "DROP TABLE IF EXISTS trees_history",
        """CREATE TABLE trees (
        tree_id SERIAL NOT NULL,
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
        tree_health VARCHAR(255) NOT NULL,
        tree_insects BOOLEAN NOT NULL,
        tree_broken BOOLEAN NOT NULL,
        tree_image VARCHAR(255) NOT NULL,
        tree_plant_date TIMESTAMP NOT NULL,
        PRIMARY KEY (tree_id)
        )
        """,
        """CREATE TABLE tree_inventory (
        InventoryID SERIAL NOT NULL,
        tree_status BOOLEAN,
        CommonName VARCHAR(255) NOT NULL,  
        BotanicalName VARCHAR(255) NOT NULL,
        PlantingOpt1 TEXT,
        PlantingOpt1Com TEXT,
        PlantingOpt2 TEXT,
        PlantingOpt2Com TEXT,
        Longitude FLOAT8 NOT NULL,
        Latitude FLOAT8 NOT NULL,
        PlantingDistrict VARCHAR(255) NOT NULL,
        Address VARCHAR(255) NOT NULL,
        Street VARCHAR(255) NOT NULL,
        SideType VARCHAR(255) NOT NULL,
        Tree INTEGER NOT NULL,
        tree_city VARCHAR(255),
        tree_state VARCHAR(255),
        tree_country VARCHAR(255),
        tree_zip VARCHAR(255),
        tree_water_level float8,
        tree_health VARCHAR(255),
        tree_insects BOOLEAN,
        tree_broken BOOLEAN,
        SelecTreeLink VARCHAR(255) NOT NULL,
        DBH VARCHAR(255) NOT NULL,
        Height VARCHAR(255),
        Owner VARCHAR(255) NOT NULL,
        PRIMARY KEY (InventoryID)
        )
        """,
        """ CREATE TABLE users (
        user_id SERIAL NOT NULL,
        user_email VARCHAR(255) NOT NULL,
        user_name VARCHAR(255) NOT NULL,
        user_password VARCHAR(255) NOT NULL,
        user_city VARCHAR(255) NOT NULL,
        user_state VARCHAR(255) NOT NULL,
        user_country VARCHAR(255) NOT NULL,
        user_zip VARCHAR(255) NOT NULL,
        user_date_created TIMESTAMP default current_timestamp,
        user_image VARCHAR(255) NOT NULL,
        PRIMARY KEY (user_id)
        )
        """,
        """ CREATE TABLE users_log (
        user_log_id SERIAL NOT NULL,
        user_id SERIAL NOT NULL,
        user_login_time TIMESTAMP NOT NULL,
        user_logout_time TIMESTAMP,
        PRIMARY KEY (user_log_id)
        )
        """,
        """ CREATE TABLE trees_history (
        tree_history_id SERIAL NOT NULL,
        tree_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        tree_history_action VARCHAR(255) NOT NULL, 
        tree_history_date TIMESTAMP default current_timestamp,
        PRIMARY KEY (tree_history_id)
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
    cur = conn.cursor()
    #tree_data = pd.read_excel('../data/trees_schema.xlsx', sheet_name='trees')
    #insert_cols = ['tree_status', 'tree_name', 'tree_scientific_name',
    #'tree_longitude', 'tree_latitude', 'tree_street_address', 'tree_city', 
    #'tree_state', 'tree_country', 'tree_zip', 'tree_water_level', 'tree_health',
    #'tree_insects', 'tree_broken', 'tree_plant_date', 'tree_image']
    #for i, row in tree_data.iterrows():
    #    insert_values = tuple(row[insert_cols].values)
    #    insert_query = """INSERT INTO {0} ({1}) VALUES {2}""".format(
    #        'trees', ", ".join(insert_cols), insert_values
    #    )
    #    print(insert_query)
    #    cur.execute(insert_query)
    tree_inventory = pd.read_excel('../data/trees_schema.xlsx', sheet_name='tree_inventory')
    insert_cols = ["InventoryID", "Address", "Street", "SideType", "Tree", 
    "CommonName", "BotanicalName", "SelecTreeLink", "DBH", "Latitude", 
    "Longitude", "Owner", "PlantingDistrict", "PlantingOpt1", "PlantingOpt1Com", 
    "PlantingOpt2", "PlantingOpt2Com"]
    for i, row in tree_inventory.iterrows():
        insert_values = tuple(row[insert_cols].values)
        insert_query = """INSERT INTO {0} ({1}) VALUES {2}""".format(
            'tree_inventory', ", ".join(insert_cols), insert_values
        )
        print(insert_query)
        cur.execute(insert_query)

    user_data = pd.read_excel('../data/trees_schema.xlsx', sheet_name='users')
    insert_cols = ['user_email', 'user_name', 'user_password', 
    'user_city', 'user_state', 'user_country', 'user_zip', 
    'user_image']
    for i, row in user_data.iterrows():
        insert_values = tuple(row[insert_cols].values)
        insert_query = """INSERT INTO {0} ({1}) VALUES {2}""".format(
            'users', ", ".join(insert_cols), insert_values
        )
        print(insert_query)
        cur.execute(insert_query)

    tree_history_data = pd.read_excel('../data/trees_schema.xlsx', sheet_name='trees_history')
    insert_cols = ['tree_id', 'user_id', 'tree_history_action']
    for i, row in tree_history_data.iterrows():
        insert_values = tuple(row[insert_cols].values)
        insert_query = """INSERT INTO {0} ({1}) VALUES {2}""".format(
            'trees_history', ", ".join(insert_cols), insert_values
        )
        print(insert_query)
        cur.execute(insert_query)
    cur.close()
    conn.commit()
    conn.close()
    return "Success"
if __name__ == '__main__':
    create_tables()
    print(load_sample_data())