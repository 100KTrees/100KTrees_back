import psycopg2 as ps
import pandas as pd
import json
#Note: A preexisting database called "100KTrees" is needed outside of this script"

"""after starting postgresql from command line (psql), i used the following lines 
to initialize the database as well as to create the user and the role
for the user -- i am not sure how to do this programatically"""
    
#CREATE DATABASE "100KTrees";
#CREATE USER user_name with encrypted password 'password';
#GRANT ALL PRIVILEGES ON DATABASE "100KTrees" TO user_name;
#ALTER USER user_name CREATEDB;

def load_configs():
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

def create_tables():
    commands = (
        "DROP TABLE IF EXISTS tree_inventory",
        "DROP TABLE IF EXISTS users",
        "DROP TABLE IF EXISTS users_log",
        "DROP TABLE IF EXISTS trees_history",
        """CREATE TABLE trees_inventory (
        InventoryID SERIAL NOT NULL,
        TreeStatus BOOLEAN,
        TreeName VARCHAR(255),
        CommonName VARCHAR(255),  
        BotanicalName VARCHAR(255),
        PlantingOpt1 VARCHAR(255),
        PlantingOpt1Com VARCHAR(255),
        PlantingOpt2 VARCHAR(255),
        PlantingOpt2Com VARCHAR(255),
        Longitude FLOAT8,
        Latitude FLOAT8,
        PlantingDistrict VARCHAR(255),
        Address VARCHAR(255),
        Street VARCHAR(255),
        SideType VARCHAR(255),
        Tree INTEGER,
        TreeCity VARCHAR(255),
        TreeState VARCHAR(255),
        TreeCountry VARCHAR(255),
        TreeZip VARCHAR(255),
        TreeWaterLevel INTEGER default 100,
        TreeHealth VARCHAR(255),
        TreeInsects BOOLEAN,
        TreeBroken BOOLEAN,
        SelecTreeLink VARCHAR(255),
        TreeImageURL VARCHAR(255),
        DBH VARCHAR(255),
        Height VARCHAR(255),
        Owner VARCHAR(255,
        PRIMARY KEY (InventoryID)
        )
        """,
        """ CREATE TABLE users (
        UserID SERIAL NOT NULL,
        UserEmail VARCHAR(255),
        UserName VARCHAR(255),
        UserPassword VARCHAR(255),
        UserCity VARCHAR(255),
        UserState VARCHAR(255),
        UserCountry VARCHAR(255),
        UserZip VARCHAR(255),
        UserDateCreated TIMESTAMP default current_timestamp,
        UserImageURL VARCHAR(255),
        PRIMARY KEY (UserID)
        )
        """,
        """ CREATE TABLE users_log (
        UserLogID SERIAL NOT NULL,
        UserID INTEGER,
        UserLoginTime TIMESTAMP,
        UserLogoutTime TIMESTAMP,
        PRIMARY KEY (UserLogID)
        )
        """,
        """ CREATE TABLE trees_history (
        TreeHistoryID SERIAL NOT NULL,
        InventoryID INTEGER,
        UserID INTEGER,
        TreeHistoryAction VARCHAR(255), 
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
    cur.close()
    conn.commit()
    conn.close()
    return "Success"
if __name__ == '__main__':
    create_tables()
    print(load_sample_data())