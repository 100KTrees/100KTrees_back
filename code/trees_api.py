from flask import Flask, request, jsonify
import psycopg2 as ps
import datetime
app = Flask(__name__)
#GET is from backend to frontend
#POST is from frontend to backend

add user_latitude, user_longitude

def load_configs():
    """
    load_configs: load the configs json
    inputs:
        None
    outputs:
        data - config json
    """

    ConfigFile = "../config/config.json"
    with open(ConfigFile, "r+") as config:
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
	if request.method == 'POST' and 'LoginUser' in request.form:
		#Ensure the user trying to login exists in the user DB
		UserEmail = request.form['UserEmail'].lower()
		UserPassword = request.form['UserPassword']
		query = """SELECT UserEmail, UserPassword 
					FROM users 
					WHERE UserEmail = {0}""".format(UserEmail)
		User = pd.read_sql(query, conn)
		if len(User) == 0:
			return jsonify(isError=True, message="email not registered as user")
		elif User["UserPassword"] != UserPassword:
			return jsonify(isError=True, message="email/password does not match")
		else:
			insert_cols = ['UserID', 'UserLoginTime']
			insert_values = (request.form['UserID'], str(datetime.now()))
			insert_query = """INSERT INTO {0} ({1}) VALUES {2}""".format(
				'users_log', ",".join(insert_cols), insert_values
				)
			cur.execute(insert_query)
			cur.close()
			conn.commit()
			conn.close()
			return jsonify(isError=False, message="Successful Login")

	#ForgotPassword
	elif request.method == 'POST' and 'ForgotPassword' in request.form:
		#Send an email to the user to reset their password
		UserEmail = request['UserEmail'].lower()
		query = """SELECT UserEmail
					FROM users
					WHERE UserEmail = {}""".format(UserEmail)
		User = pd.read_sql(query, conn)
		if len(User) == 0:
			return jsonify(isError=True, message="email address not found")
		else:
			#TODO: some logic about sending an email for password reset needed here
			return jsonify(isError=False, message="email sent to reset password")

	#LogoutUser
	elif request.method == 'POST' and 'LogoutUser' in request.form:
		#Update the most recent login entry for a user with their logout time
		UserEmail = request.form['UserEmail']
		query = """SELECT UserID 
					FROM users 
					WHERE UserEmail={0}""".format(UserEmail)
		UserID = pd.real_sql(query, conn)
		UserID = UserID['UserID'].values[0]
		query = """SELECT UserLogID, 
					FROM users_log 
					WHERE UserID={0}""".format(UserID)
		UserLogID = pd.read_sql(query, conn)
		UserLogID = userLogID['UserLogID'].max()
		insert_cols = ['UserLogID', 'UserLogoutTime']
		insert_values = (UserLogID, str(datetime.now()))
		insert_query = """INSERT INTO {0} ({1}) VALUES {2}""".format(
			'users_log', ",".join(insert_cols), insert_values
			)
		cur.execute(insert_query)
		cur.close()
		conn.commit()
		conn.close()
		return jsonify(isError=False, message='Successful Logout')

	#GetUser
	elif request.method == 'GET' and 'UserName' in request.form:
		UserName = request.form['UserName'].lower()
		query = """SELECT UserEmail 
					FROM users 
					WHERE UserName = {0}""".format(UserName)
		User = pd.read_sql(query, conn)
		if len(User) == 0:
			return jsonify(isError=True, message="Please Login Again")
		else:
			return jsonify(isError=False, User['UserEmail'].values)

	#GetUserHistory
	elif request.method == 'GET' and 'GetUserHistory' in request.form:
		UserName = request.form['UserName']
		query = """SELECT UserID 
					FROM users 
					WHERE UserName={0}""".format(UserName)
		UserID = pd.read_sql(query, conn)
		if len(UserID)==0:
			return jsonify(isError=True, message="User name does not exist")
		else:
			query = """SELECT UserID, InventoryID, TreeHistoryAction, TreeHistoryDate 
					FROM trees_history
					WHERE UserID={0}""".format(user_id)
			UserTreeHistory = pd.read_sql(query, conn)
			UserTreeHistory = UserTreeHistory.sort_values('TreeHistoryDate')
			UserTreeHistory = UserTreeHistory.values
			return jsonify(isError=False, UserTreeHistory)

	#CreateUser
	elif request.method = 'POST' and 'CreateUser' in request.form:
		UserName = request.form['UserName'].lower()
		UserEmail = request.form['UserEmail'].lower()
		UserPassword = request.form['UserPassword']
		UserCity = request.form['UserCity']
		UserState = request.form['UserState']
		UserCountry = request.form['UserCountry']
		UserDateCreated = request.form['UserDateCreated']
		UserImageURL = request.form['UserImageURL']
		query = """SELECT UserName 
					FROM users 
					WHERE UserName = {0}""".format(UserName)
		UserNameCheck = pd.read_sql(query, conn)
		query = """SELECT UserEmail 
					FROM users 
					WHERE UserName = {0}""".format(UserName)
		UserEmailCheck = pd.read_sql(query, conn)
		if len(UserNameCheck) > 0:
			return jsonify(isError=True, message="Duplicate username")
		elif len(UserEmailCheck) != 0:
			return jsonify(isError=True, message="Duplicate email")
		else:
			insert_cols = ['UserName', 'UserEmail', 'UserPassword',
							'UserCity', 'UserState', 'UserCountry',
							'UserDateCreated', 'UserImageURL']
			insert_values = [UserName, UserEmail, UserPassword,
							UserCity, UserState, UserCountry,
							UserDateCreated, UserImageURL]
			insert_query = """INSERT INTO {0} ({1}) VALUES {2}""".format(
			'users', ",".join(insert_cols), insert_values
			)
			cur.execute(insert_query)
			cur.close()
			conn.commit()
			conn.close()
			return jsonify(isError=False, "Account successfully created")

	#GetUserProfile
	elif request.method = 'POST' and 'GetUserProfile' in request.form:
		UserName = request.form['UserName'].lower()
		query = """SELECT UserName, UserImageURL, UserCity, UserState, UserZip
					FROM users 
					WHERE UserName = {0}""".format(UserName)
		UserProfile = pd.read_sql(query, conn)
		UserImageURL = user_profile['UserImageURL']
		UserLocation = user_profile[['UserCity', 'UserState', 'UserZip']].values

		query = """SELECT InventoryID, TreeHistoryAction, TreeHistoryActionDate
					FROM trees_history 
					WHERE UserName = {0}""".format(user_name)
		TreeUserHistory = pd.read_sql(query, conn)
		TreeList = TreeUserHistory['InventoryID'].unique()
		TreesWateredSum = len(TreeUserHistory[TreeUserHistory['TreeHistoryAction'] == 'Watered'])
		TreesPlantedSum = len(TreeUserHistory[TreeUserHistory['TreeHistoryAction'] == 'Planted'])
		TreesIdentifiedSum = len(TreeUserHistory[TreeUserHistory['TreeHistoryAction'] == 'Identified'])
		AchievementSum = TreesWateredSum + TreesPlantedSum + TreesIdentifiedSum
		UserTreeList = [UserImageURL, UserName, AchievementSum, TreesWateredSum, 
						TreesPlantedSum, TreesIdentifiedSum]
		return jsonify(isError=False, UserLocation, UserTreeList)

	#InviteFriend
	elif request.method = 'GET' and 'InviteFriend' in request.form:
		#Not sure of what the functionality should be for API here
		return jsonify(isError=True, message='not implemented')

@app.route("/tree", methods=['POST', 'GET'])
def Tree():
	conn = get_conn()
	cur = conn.cursor()
	#CreateTree
	if request.method = 'POST' and 'CreateTree' in request.form:
		TreeStatus = request.form['TreeStatus']
		TreeName = request.form['TreeName']
		CommonName = request.form['CommonName']
		BotanicalName = request.form['BotanicalName']
		Longitude = request.form['Longitude']
		Latitude = request.form['Latitude']
		Address = request.form['Address']
		Street = request.form['Street']
		TreeCity = request.form['tree_city']
		TreeState = request.form['tree_state']
		TreeCountry = request.form['tree_country']
		TreeZip = request.form['tree_zip']
		TreeWaterLevel = request.form['tree_water_level']
		TreeHealth = request.form['tree_health']
		TreeInsects = request.form['tree_insects']
		TreeBroken = request.form['tree_broken']
		TreePlantDate = request.form['tree_plant_date']
		SelecTreeLink = request.form['SelecTreeLink']
		create_cols = ['TreeStatus', 'TreeName',
					'CommonName', 'BotanicalName', 'Longitude',
					'Latitude', 'Address', 'Street', 'TreeCity',
					'TreeState', 'TreeCountry', 'TreeZip', 
					'TreeWaterLevel', 'TreeHealth', 'TreeInsects',
					'TreeBroken', 'TreePlantDate', 'SelecTreeLink']
		create_values = [TreeStatus, TreeName,
					CommonName, BotanicalName, Longitude,
					Latitude, Address, Street, TreeCity,
					TreeState, TreeCountry, TreeZip, 
					TreeWaterLevel, TreeHealth, TreeInsects,
					TreeBroken, TreePlantDate, SelecTreeLink]
		create_query = """INSERT INTO {0} ({1}) VALUES {2}""".format(
			'trees_inventory', ",".join(create_cols), create_values)
		cur.execute(create_query)
		action_cols = ['InventoryID', 'UserID', 'TreeHistoryAction']
		action_values = [InventoryID, UserID, "Identified"]
		action_query = """INSERT INTO {0} ({1}) VALUES {2}""".format(
		'trees_history', ",".join(action_cols), action_values)
		cur.execute(insert_query)
		cur.close()
		conn.commit()
		conn.close()
		return jsonify(isError=False, message="Tree successfully created")

	#PostTree
	elif request.method = 'POST' and 'PostTree' in request.form:
		InventoryID = request.form['InventoryID']
		TreeStatus = request.form['TreeStatus']
		TreeName = request.form['TreeName']
		CommonName = request.form['CommonName']
		BotanicalName = request.form['BotanicalName']
		Longitude = request.form['Longitude']
		Latitude = request.form['Latitude']
		Address = request.form['Address']
		Street = request.form['Street']
		TreeCity = request.form['tree_city']
		TreeState = request.form['tree_state']
		TreeCountry = request.form['tree_country']
		TreeZip = request.form['tree_zip']
		TreeWaterLevel = request.form['tree_water_level']
		TreeHealth = request.form['tree_health']
		TreeInsects = request.form['tree_insects']
		TreeBroken = request.form['tree_broken']
		TreePlantDate = request.form['tree_plant_date']
		SelecTreeLink = request.form['SelecTreeLink']
		UserID = request.form['user_id']
		query = "SELECT user_id FROM users WHERE user_id = {}".format(user_id)
		UserCheck = pd.read_sql(query, conn)
		if len(UserCheck) == 0:
			return jsonify(isError=True, message="Login to update tree")
		query = "SELECT InventoryID FROM trees_inventory WHERE InventoryID={}".format(InventoryID)
		TreeCheck = pd.read_sql(query, conn)
		if len(TreeCheck) > 0:
			update_cols = ['InventoryID', 'TreeStatus', 'TreeName',
						'CommonName', 'BotanicalName', 'Longitude',
						'Latitude', 'Address', 'Street', 'TreeCity',
						'TreeState', 'TreeCountry', 'TreeZip', 
						'TreeWaterLevel', 'TreeHealth', 'TreeInsects',
						'TreeBroken', 'TreePlantDate', 'SelecTreeLink']
			update_values = [InventoryID, TreeStatus, TreeName,
						CommonName, BotanicalName, Longitude,
						Latitude, Address, Street, TreeCity,
						TreeState, TreeCountry, TreeZip, 
						TreeWaterLevel, TreeHealth, TreeInsects,
						TreeBroken, TreePlantDate, SelecTreeLink]
			update_query = """UPDATE trees_inventory  
					SET {0} VALUES ({1})""".format(",".join(update_cols), update_values)
			cur.execute(update_query)
			cur.close()
			conn.commit()
			conn.close()
			return jsonify(isError=False, message="Tree successfully updated")
		else:
			return jsonify(isError=True, message="Tree must be created")

	#GetTreeList
	if request.method = 'GET' and 'GetTreeList' in request.form:
		query = """SELECT DISTINCT CommonName
				FROM trees_inventory"""
		TreeList = pd.read_sql(query, conn)
		TreeList = TreeList.values
		if len(TreeList) == 0:
			return jsonify(isError=False, message="No unique tree common names")
		else:
			return jsonify(isError=False, TreeList)

	#GetTree
	if request.method = 'GET' and 'GetTree' in request.form:
		InventoryID = request.form['InventoryID']
		query = """SELECT * FROM trees_inventory 
				WHERE InventoryID = {0}""".format(InventoryID)
		TreeRecord = pd.read_sql(query, conn)
		TreeRecord = TreeRecord.values
		if len(TreeRecord) == 0:
			return jsonify(isError=True, message="Tree does not exist")	
		return jsonify(isError=False, TreeRecord)

	#GetTreeHistory
	if request.method = 'GET' and 'GetTreeHistory' in request.form:
		InventoryID = request.form['InventoryID']
		query = """SELECT tree_history_action, tree_history_action_date
				FROM trees_history 
				WHERE InventoryID = {0}""".format(InventoryID)
		TreeHistory = pd.read_sql(query, conn)
		if len(TreeHistory) == 0:
			return jsonify(isError=True, message="Tree has no history")
		else:
			TreeHistory = TreeHistory.sort_values('tree_history_action_date')
			TreeHistory = TreeHistory.values
			return jsonify(isError=False, TreeHistory)


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