# 100KTrees

## Quick Start
## To get started, you need to start PostGresSQl and create the 100KTrees Database.
## You can create the environment that is contained in the environment.yml file to ensure dependancies are all installed on your machine. 

#### Get the latest version

Clone the latest version of the Portal to your machine by running:

```shell
$ git clone https://github.com/100KTrees/100KTrees_back.git
$ cd 100KTrees_back
$ pip install psycopg2
$ pip install pandas
$ pip install flask
$ pip install xlrd
```

## This information helped me get started with PostGres on Mac:
## https://www.codementor.io/@engineerapart/getting-started-with-postgresql-on-mac-osx-are8jcopb 
## https://chartio.com/resources/tutorials/how-to-start-postgresql-server-on-mac-os-x/ 

## Once Postgres is installed, you can then start an instance from command line as shown in the tutorial above.
## The following is what can be used to create the database: 

```shell
$ cd code
$ python create_database.py
```
 
CREATE DATABASE "100KTrees";
CREATE USER user_name with encrypted password 'password';
GRANT ALL PRIVILEGES ON DATABASE "100KTrees" TO user_name;
ALTER USER user_name CREATEDB;


#### START UP THE API SERVER
```shell
$ python trees_api.py
```

## Now you should be able to run create_database.py to create all of the tables needed for the backend, and populate the inventory table with the data that is contained in trees_schema.xlsx (needs to be updated to reflect current table structures)

## Finally, you can run trees_api.py to start up the API services that should speak to and hear from the front-end (at some point)
