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
		email = request.form['email']
		query = """SELECT user_id FROM users WHERE user_email={0}""".format(email)
		user_id = pd.real_sql(query, conn)
		insert_cols = ['user_id', 'user_logout_time']
		insert_values = (user_id, str(datetime.now()))
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
			query = """SELECT user_id, tree_id, tree_history_action, tree_history_date 
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

		query = """SELECT tree_id, tree_history_action, tree_history_action_date
					FROM trees_history 
					WHERE user_name = {0}""".format(user_name)
		tree_user_history = pd.read_sql(query, conn)
		tree_list = tree_user_history['tree_id'].unique()
		trees_watered_sum = len(tree_user_history[tree_user_history['tree_history_action'] == 'Watered'])
		trees_planted_sum = len(tree_user_history[tree_user_history['tree_history_action'] == 'Planted'])
		achievement_sum = trees_watered_sum + trees_planted_sum
		user_tree_list = [user_photo, user_name, achievement_sum, trees_watered_sum, 
							trees_planted_sum]
		return jsonify(isError=False, user_location, user_tree_list)

	#invteFriend
	elif request.method = 'GET' and 'invite_friend' in request.form:
		

@app.route("/postTree", methods=['POST'])
def postTree():
	"""
	Get the tree information from db and return it to the post upon sucess
	"""
	try:
		data = request.data
		#put this data into the trees table in 100K database

		return jsonify(isError=False, message="posted tree success into DB", statusCode=200)
	except:
		return jsonify(isError=True, message="failure")

@app.route("/postUserCreate", methods=['POST'])
def postUserCreate():
	try:
		data = request.data
		#put this data into the user table in 100K database

		return jsonify(isError=False, message="posted tree success into DB", statusCode=200)
	except:
		return jsonify(isError=True, message="failure")

@app.route("/getTree", methods=['GET'])
def getTree():
	try:
		data = request.data
		#Make query out of this data and query the trees table in 100K database
		#return data from query as data

		return jsonify(isError=False, message="Success", statusCode= 200, data=data)
	except:
		return jsonify(isError=True, message="failure")

@app.route("/getHistoryTree", methods=['GET'])
def getHistoryTree():
	try:
		data = request.data
		#Make query out of this data and query the trees table in 100K database
		#return the data from query as data

		return jsonify(isError=False, message="Success", statusCode=200, data=data)
	except:
		return jsonify(isError=True, message="failure")

@app.route("/getHistoryUser", methods=['GET'])
def getHistoryUser():
	try:
		data = request.data
		#Make query out of this data and query the trees table in 100K database
		#return the data from query as data

		return jsonify(isError=False, message="Success", statusCode=200, data=data)
	except:
		return jsonify(isError=True, message="failure")

@app.route("/getMap", methods=['GET'])
def getMap():
	try:
		data = request.data
		#Make query out of this data and query the trees table in 100K database
		#return the data from the query as data

		return jsonify(isError=False, message="Success", statusCode=200, data=data)
	except:
		return jsonify(isError=True, message="failure")

@app.route("/getUserProfile", methods=['GET'])
def getUserProfile():
	try:
		data = request.data
		return jsonify(isError=False, message="Success", statusCode=200, data=data)
	except:
		return jsonify(isError=True, message="failure")


if __name__ == '__main__':
	app.run(port=30000)