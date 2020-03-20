from flask import Flask, request, jsonify
import psycopg2 as ps
import datetime
app = Flask(__name__)
#GET is from backend to frontend
#POST is from frontend to backend

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

@app.route("/user", methods=['POST', 'GET'])
def User():
	"""
	All of the API calls pertaining to the user page
	"""
	conn = get_conn()
	cur = conn.cursor()

	#loginUser
	if request.method == 'POST' and 'loginuser' in request.form:
		#Ensure the user trying to login exists in the user DB
		email = request.form['email'].lower()
		pasword = request.form['encoded_password']
		query = """SELECT user_email, user_password 
					FROM users 
					WHERE user_email = {0}""".format(email)
		user = pd.read_sql(query, conn)
		if len(user) == 0:
			return jsonify(isError=True, message="email not registered as user")
		elif user["user_password"] != password:
			return jsonify(isError=True, message="email/password does not match")
		else:
			insert_cols = ['user_id', 'user_login_time']
			insert_values = (request.form['user'], str(datetime.now()))
			insert_query = """INSERT INTO {0} ({1}) VALUES {2}""".format(
				'users_log', ",".join(insert_cols), insert_values
				)
			cur.execute(insert_query)
			cur.close()
			conn.commit()
			conn.close()
			return jsonify(isError=False, message="Successful Login")

	#forgotPassword
	elif request.method == 'POST' and 'forgot_password' in request.form:
		#Send an email to the user to reset their password
		email = request['email'].lower()
		query = """SELECT user_email
					FROM users
					WHERE user_email = {}""".format(email)
		user = pd.read_sql(query, conn)
		if len(user) == 0:
			return jsonify(isError=True, message="email address not found")
		else:
			#TODO: some logic about sending an email for password reset needed here
			return jsonify(isError=False, message="email sent to reset password")

	#logout
	elif request.method == 'POST' and 'logout' in request.form:
		#Update the most recent login entry for a user with their logout time
		email = request.form['email']
		query = """SELECT user_id 
					FROM users 
					WHERE user_email={0}""".format(email)
		user_id = pd.real_sql(query, conn)
		user_id = user_id['user_id'].values[0]
		query = """SELECT user_log_id, 
					FROM users_log 
					WHERE user_id={0}""".format(user_id)
		user_log_id = pd.read_sql(query, conn)
		user_log_id = user_log_id['user_log_id'].max()
		insert_cols = ['user_log_id', 'user_logout_time']
		insert_values = (user_log_id, str(datetime.now()))
		insert_query = """INSERT INTO {0} ({1}) VALUES {2}""".format(
			'users_log', ",".join(insert_cols), insert_values
			)
		cur.execute(insert_query)
		cur.close()
		conn.commit()
		conn.close()
		return jsonify(isError=False, message='Successful Logout')

	#user
	elif request.method == 'GET' and 'user_name' in request.form:
		username = request.form['user_name'].lower()
		query = """SELECT user_email 
					FROM users 
					WHERE user_name = {0}""".format(username)
		user = pd.read_sql(query, conn)
		if len(user) == 0:
			return jsonify(isError=True, message="Please Login Again")
		else:
			return jsonify(isError=False, message=user['user_email'])

	#getUserHistory
	elif request.method == 'GET' and 'user_history' in request.form:
		user_name = request.form['user_name']
		query = """SELECT user_id 
					FROM users 
					WHERE user_name={0}""".format(user_name)
		user_id = pd.read_sql(query, conn)
		if len(user_id)==0:
			return jsonify(isError=True, message="User name does not exist")
		else:
			query = """SELECT user_id, InventoryID, tree_history_action, tree_history_date 
					FROM trees_history
					WHERE user_id={0}""".format(user_id)
			user_tree_history = pd.read_sql(query, conn)
			user_tree_history = user_tree_history.sort_values('tree_history_date')
			user_tree_history = user_tree_history.values
			return jsonify(isError=False, user_tree_history)

	#createUser
	elif request.method = 'POST' and 'create_user' in request.form:
		user_name = request.form['user_name'].lower()
		user_email = request.form['user_email'].lower()
		user_password = request.form['user_password']
		user_city = request.form['user_city']
		user_state = request.form['user_state']
		user_country = request.form['user_country']
		user_date_created = request.form['user_date_created']
		user_photo = request.form['user_photo']
		query = """SELECT user_name 
					FROM users 
					WHERE user_name = {0}""".format(user_name)
		user_name_check = pd.read_sql(query, conn)
		query = """SELECT user_email 
					FROM users 
					WHERE user_name = {0}""".format(user_name)
		user_email_check = pd.read_sql(query, conn)
		if len(user_name_check) != 0:
			return jsonify(isError=True, message="Duplicate username")
		elif len(user_email_check) != 0:
			return jsonify(isError=True, message="Duplicate email")
		else:
			insert_cols = ['user_name', 'user_email', 'user_password',
							'user_city', 'user_state', 'user_country',
							'user_date_created', 'user_photo']
			insert_values = [user_name, user_email, user_password,
							user_city, user_state, user_country,
							user_date_created, user_photo]
			insert_query = """INSERT INTO {0} ({1}) VALUES {2}""".format(
			'users', ",".join(insert_cols), insert_values
			)
			cur.execute(insert_query)
			cur.close()
			conn.commit()
			conn.close()
			return jsonify(isError=False, "Account successfully created")

	#getUserProfile
	elif request.method = 'POST' and 'user_profile' in request.form:
		user_name = request.form['user_name'].lower()
		query = """SELECT user_name, user_photo, user_city, user_state, user_zip
					FROM users 
					WHERE user_name = {0}""".format(user_name)
		user_profile = pd.read_sql(query, conn)
		user_photo = user_profile['user_photo']
		user_location = user_profile[['user_city', 'user_state', 'user_zip']].values

		query = """SELECT InventoryID, tree_history_action, tree_history_action_date
					FROM trees_history 
					WHERE user_name = {0}""".format(user_name)
		tree_user_history = pd.read_sql(query, conn)
		tree_list = tree_user_history['InventoryID'].unique()
		trees_watered_sum = len(tree_user_history[tree_user_history['tree_history_action'] == 'Watered'])
		trees_planted_sum = len(tree_user_history[tree_user_history['tree_history_action'] == 'Planted'])
		tree_identified_sum = len(tree_user_history[tree_user_history['tree_history_action'] == 'Identified'])
		achievement_sum = trees_watered_sum + trees_planted_sum + tree_identified_sum
		user_tree_list = [user_photo, user_name, achievement_sum, trees_watered_sum, 
							trees_planted_sum, tree_identified_sum]
		return jsonify(isError=False, user_location, user_tree_list)

	#invteFriend
	elif request.method = 'GET' and 'invite_friend' in request.form:
		#Not sure of what the functionality should be for API here
		return jsonify(isError=True, message='not implemented')

@app.route("/tree", methods=['POST', 'GET'])
def Tree():
	conn = get_conn()
	cur = conn.cursor()
	if request.method = 'POST' and 'posttree' in request.form:
		InventoryID = request.form['InventoryID']
		tree_status = request.form['tree_status']
		tree_name = request.form['tree_name']
		CommonName = request.form['CommonName']
		BotanicalName = request.form['BotanicalName']
		Longitude = request.form['Longitude']
		Latitude = request.form['Latitude']
		Address = request.form['Address']
		Street = request.form['Street']
		tree_city = request.form['tree_city']
		tree_state = request.form['tree_state']
		tree_country = request.form['tree_country']
		tree_zip = request.form['tree_zip']
		tree_water_level = request.form['tree_water_level']
		tree_health = request.form['tree_health']
		tree_insects = request.form['tree_insects']
		tree_broken = request.form['tree_broken']
		tree_plant_date = request.form['tree_plant_date']
		SelecTreeLink = request.form['SelecTreeLink']
		user_id = request.form['user_id']
		query = "SELECT user_id FROM users WHERE user_id = {}".format(user_id)
		users = pd.read_sql(query, conn)
		if len(users) == 0:
			return jsonify(isError=True, message="Login to create tree") 

		insert_cols = ['InventoryID', 'tree_status', 'tree_name',
						'CommonName', 'BotanicalName', 'Longitude',
						'Latitude', 'Address', 'Street', 'tree_city',
						'tree_state', 'tree_country', 'tree_zip', 
						'tree_water_level', 'tree_health', 'tree_insects',
						'tree_broken', 'tree_plant_date', 'SelecTreeLink'
						]
		insert_values = [InventoryID, tree_status, tree_name,
						CommonName, BotanicalName, Longitude,
						Latitude, Address, Street, tree_city,
						tree_state, tree_country, tree_zip, 
						tree_water_level, tree_health, tree_insects,
						tree_broken, tree_plant_date, SelecTreeLink]
		insert_query = """INSERT INTO {0} ({1}) VALUES {2}""".format(
		'trees_inventory', ",".join(insert_cols), insert_values
		)
		cur.execute(insert_query)

		insert_cols = ['InventoryID', 'user_id', 'tree_history_action']
		insert_values = [InventoryID, user_id, "Identified"]
		insert_query = """INSERT INTO {0} ({1}) VALUES {2}""".format(
		'trees_history', ",".join(insert_cols), insert_values
		)
		cur.execute(insert_query)
		cur.close()
		conn.commit()
		conn.close()
		return jsonify(isError=False, message="Tree successfully posted")
	if request.method = 'GET' and 'tree_history' in request.form:
		InventoryID = request.form['InventoryID']
		query = """SELECT tree_history_action, tree_history_action_date
				FROM trees_history 
				WHERE InventoryID = {}""".format(InventoryID)
		tree_history = pd.read_sql(query, conn)
		tree_history = tree_history.sort_values('tree_history_action_date')
		tree_history = tree_history.values
		return jsonify(isError=False, tree_history)



@app.route("/getMap", methods=['GET'])
def getMap():
	try:
		data = request.data
		#Make query out of this data and query the trees table in 100K database
		#return the data from the query as data

		return jsonify(isError=False, message="Success", statusCode=200, data=data)
	except:
		return jsonify(isError=True, message="failure")


if __name__ == '__main__':
	app.run(port=30000)