from flask import Flask, request, jsonify
import psycopg2 as ps
app = Flask(__name__)
#GET is from backend to frontend
#POST is from frontend to backend

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