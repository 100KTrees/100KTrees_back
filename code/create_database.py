import psycopg2 as ps
import pandas as pd
import json
#Note: A preexisting database called "100KTrees" is needed outside of this script"

def create_database():
    """after starting postgresql from command line (psql), i used the following lines 
    to initialize the database as well as to create the user and the role
    for the user -- i am not sure how to do this programatically"""
    
    #CREATE DATABASE "100KTrees";
    #CREATE USER user_name with encrypted password 'password';
    #GRANT ALL PRIVILEGES ON DATABASE "100KTrees" TO user_name;

    #ALTER USER user_name CREATEDB;
    return

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
        "DROP TABLE IF EXISTS users",
        "DROP TABLE IF EXISTS users_log",
        "DROP TABLE IF EXISTS trees_history",
        """CREATE TABLE trees_inventory (
        InventoryID SERIAL NOT NULL,
        TreeStatus BOOLEAN,
        TreeName VARCHAR(255),
        CommonName VARCHAR(255) NOT NULL,  
        BotanicalName VARCHAR(255) NOT NULL,
        PlantingOpt1 VARCHAR(255),
        PlantingOpt1Com VARCHAR(255),
        PlantingOpt2 VARCHAR(255),
        PlantingOpt2Com VARCHAR(255),
        Longitude FLOAT8 NOT NULL,
        Latitude FLOAT8 NOT NULL,
        PlantingDistrict VARCHAR(255),
        Address VARCHAR(255) NOT NULL,
        Street VARCHAR(255) NOT NULL,
        SideType VARCHAR(255),
        Tree INTEGER,
        TreeCity VARCHAR(255),
        TreeState VARCHAR(255),
        TreeCountry VARCHAR(255),
        TreeZip VARCHAR(255),
        TreeWaterLevel FLOAT8,
        TreeHealth VARCHAR(255),
        TreeInsects BOOLEAN,
        TreeBroken BOOLEAN,
        SelecTreeLink VARCHAR(255) NOT NULL,
        TreeImageURL VARCHAR(255),
        DBH VARCHAR(255),
        Height VARCHAR(255),
        Owner VARCHAR(255,
        PRIMARY KEY (InventoryID)
        )
        """,
        """ CREATE TABLE users (
        UserID SERIAL NOT NULL,
        UserEmail VARCHAR(255) NOT NULL,
        UserName VARCHAR(255) NOT NULL,
        UserPassword VARCHAR(255) NOT NULL,
        UserCity VARCHAR(255) NOT NULL,
        UserState VARCHAR(255) NOT NULL,
        UserCountry VARCHAR(255) NOT NULL,
        UserZip VARCHAR(255) NOT NULL,
        UserDateCreated TIMESTAMP default current_timestamp,
        UserImageURL VARCHAR(255) NOT NULL,
        PRIMARY KEY (UserID)
        )
        """,
        """ CREATE TABLE users_log (
        UserLogID SERIAL NOT NULL,
        UserID INTEGER NOT NULL,
        UserLoginTime TIMESTAMP NOT NULL,
        UserLogoutTime TIMESTAMP,
        PRIMARY KEY (UserLogID)
        )
        """,
        """ CREATE TABLE trees_history (
        TreeHistoryID SERIAL NOT NULL,
        InventoryID INTEGER NOT NULL,
        UserID INTEGER NOT NULL,
        TreeHistoryAction VARCHAR(255) NOT NULL, 
        TreeHistoryDate TIMESTAMP default current_timestamp,
        PRIMARY KEY (TreeHistoryID)
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
    tree_inventory = pd.read_excel('../data/trees_schema.xlsx', sheet_name='tree_inventory')
    insert_cols = ["InventoryID", "Address", "Street", "SideType", "Tree", 
    "CommonName", "BotanicalName", "SelecTreeLink", "DBH", "Latitude", 
    "Longitude", "Owner", "PlantingDistrict", "PlantingOpt1", "PlantingOpt1Com", 
    "PlantingOpt2", "PlantingOpt2Com"]
    for i, row in tree_inventory.iterrows():
        insert_values = tuple(row[insert_cols].values)
        insert_query = """INSERT INTO {0} ({1}) VALUES {2}""".format(
            'trees_inventory', ", ".join(insert_cols), insert_values
        )
        print(insert_query)
        cur.execute(insert_query)

    #user_data = pd.read_excel('../data/trees_schema.xlsx', sheet_name='users')
    #insert_cols = ['user_email', 'user_name', 'user_password', 
    #'user_city', 'user_state', 'user_country', 'user_zip', 
    #'user_image']
    #for i, row in user_data.iterrows():
    #    insert_values = tuple(row[insert_cols].values)
    #    insert_query = """INSERT INTO {0} ({1}) VALUES {2}""".format(
    #        'users', ", ".join(insert_cols), insert_values
    #    )
    #    print(insert_query)
    #    cur.execute(insert_query)

    #tree_history_data = pd.read_excel('../data/trees_schema.xlsx', sheet_name='trees_history')
    #insert_cols = ['tree_id', 'user_id', 'tree_history_action']
    #for i, row in tree_history_data.iterrows():
    #    insert_values = tuple(row[insert_cols].values)
    #    insert_query = """INSERT INTO {0} ({1}) VALUES {2}""".format(
    #        'trees_history', ", ".join(insert_cols), insert_values
    #    )
    #    print(insert_query)
    #    cur.execute(insert_query)
    cur.close()
    conn.commit()
    conn.close()
    return "Success"
if __name__ == '__main__':
    create_tables()
    print(load_sample_data())