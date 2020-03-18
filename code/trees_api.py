from flask import Flask, request, jsonify
import psycopg2 as ps
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
def loginUser():
	"""
	Get the tree information from db and return it to the post upon sucess
	"""
	if request.method == 'POST':
		conn = get_conn()
		try:
			email = request.form['email'].lower()
			pasword = request.form['password']
			query = """SELECT user_email, user_password 
						FROM users 
						WHERE user_email = {}""".format(email)
			user = pd.read_sql(query, conn)
			if len(user) == 0:
				return jsonify(authfail=True, error="email not registered as user")
			elif user["user_password"] != password:
				return jsonify(authfail=True, error="email/password does not match")
			else:
				return jsonify(authfail=False, message="Successful Login")
		except:
			return jsonify(isError=True, message="failure on data acquisition")
	else:
		return jsonify(isError=True, message="Method not post")

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
	app.run()