import psycopg2 as ps
import pandas as pd
import datetime
import json
from flask import Flask, request, jsonify

app = Flask(__name__)


def load_configs():
    ConfigFile = "../config/config.json"
    with open(ConfigFile, "r+") as config:
        data = json.load(config)
    return data


def get_conn():
    params = load_configs()
    conn = ps.connect(
        dbname=params["dbname"],
        user=params["user"],
        host=params["host"],
        password=params["password"],
    )
    return conn


@app.route("/user", methods=["POST", "GET"])
def User():
    conn = get_conn()
    cur = conn.cursor()

    # loginUser
    if request.method == "POST" and "LoginUser" in request.form:
        # Ensure the user trying to login exists in the user DB
        UserEmail = request.form["UserEmail"].lower()
        UserPassword = request.form["UserPassword"]
        query = """SELECT
                   UserEmail, UserPassword FROM users WHERE UserEmail =
                   {0}""".format(
            UserEmail
        )
        User = pd.read_sql(query, conn)
        if len(User) == 0:
            returnable = {"isError": True, "message": "email not registered as user"}
            return jsonify(returnable)
        elif User["UserPassword"] != UserPassword:
            returnable = {"isError": True, "message": "email/password does not match"}
            return jsonify(returnable)
        else:
            insert_cols = ["UserID", "UserLoginTime"]
            insert_values = (request.form["UserID"], str(datetime.datetime.now()))
            insert_query = """INSERT INTO {0} ({1}) VALUES {2}""".format(
                "users_log", ",".join(insert_cols), insert_values
            )
            cur.execute(insert_query)
            cur.close()
            conn.commit()
            conn.close()
            returnable = {"isError": False, "message": "Successful Login"}
            return jsonify(returnable)

    # ForgotPassword
    elif request.method == "POST" and "ForgotPassword" in request.form:
        # Send an email to the user to reset their password
        UserEmail = request["UserEmail"].lower()
        query = """SELECT UserEmail
                    FROM users
                    WHERE UserEmail = {}""".format(
            UserEmail
        )
        User = pd.read_sql(query, conn)
        if len(User) == 0:
            return jsonify(isError=True, message="email address not found")
        else:
            # TODO: some logic about sending an email for password reset needed here
            returnable = {"isError": False, "message": "email sent to reset password"}
            return jsonify(returnable)

    # LogoutUser
    elif request.method == "POST" and "LogoutUser" in request.form:
        # Update the most recent login entry for a user with their logout time
        UserEmail = request.form["UserEmail"]
        query = """SELECT UserID
                    FROM users
                    WHERE UserEmail={0}""".format(
            UserEmail
        )
        UserID = pd.read_sql(query, conn)
        UserID = UserID["UserID"].values[0]
        query = """SELECT UserLogID,
                    FROM users_log
                    WHERE UserID={0}""".format(
            UserID
        )
        UserLogID = pd.read_sql(query, conn)
        UserLogID = UserLogID["UserLogID"].max()
        insert_cols = ["UserLogID", "UserLogoutTime"]
        insert_values = (UserLogID, str(datetime.datetime.now()))
        insert_query = """INSERT INTO {0} ({1}) VALUES {2}""".format(
            "users_log", ",".join(insert_cols), insert_values
        )
        cur.execute(insert_query)
        cur.close()
        conn.commit()
        conn.close()
        returnable = {"isError": False, "message": "Successful Logout"}
        return jsonify(returnable)

    # GetUser
    elif request.method == "GET" and "UserName" in request.form:
        UserName = request.form["UserName"].lower()
        query = """SELECT UserEmail
                    FROM users
                    WHERE UserName = {0}""".format(
            UserName
        )
        User = pd.read_sql(query, conn)
        if len(User) == 0:
            returnable = {"isError": True, "message": "Please Login Again"}
            return jsonify(returnable)
        else:
            return jsonify(isError=False, UserEmail=User["UserEmail"].values)

    # GetUserHistory
    elif request.method == "GET" and "GetUserHistory" in request.form:
        UserName = request.form["UserName"]
        query = """SELECT UserID
                    FROM users
                    WHERE UserName={0}""".format(
            UserName
        )
        UserID = pd.read_sql(query, conn)
        if len(UserID) == 0:
            return jsonify(isError=True, message="User name does not exist")
        else:
            query = """SELECT UserID, InventoryID, TreeHistoryAction, TreeHistoryDate
                    FROM trees_history
                    WHERE UserID={0}""".format(
                UserID
            )
            UserTreeHistory = pd.read_sql(query, conn)
            UserTreeHistory = UserTreeHistory.sort_values("TreeHistoryDate")
            UserTreeHistory = UserTreeHistory.values
            returnable = {"isError": False, "UserTreeHistory": UserTreeHistory}
            return jsonify(returnable)

    # CreateUser
    elif request.method == "POST" and "CreateUser" in request.form:
        UserName = request.form["UserName"].lower()
        UserEmail = request.form["UserEmail"].lower()
        UserPassword = request.form["UserPassword"]
        UserCity = request.form["UserCity"]
        UserState = request.form["UserState"]
        UserCountry = request.form["UserCountry"]
        UserDateCreated = request.form["UserDateCreated"]
        UserImageURL = request.form["UserImageURL"]
        query = """SELECT UserName
                    FROM users
                    WHERE UserName = {0}""".format(
            UserName
        )
        UserNameCheck = pd.read_sql(query, conn)
        query = """SELECT UserEmail
                    FROM users
                    WHERE UserName = {0}""".format(
            UserName
        )
        UserEmailCheck = pd.read_sql(query, conn)
        if len(UserNameCheck) > 0:
            returnable = {"isError": True, "message": "Duplicate username"}
            return jsonify(returnable)
        elif len(UserEmailCheck) != 0:
            returnable = {"isError": True, "message": "Duplicate email"}
            return jsonify(returnable)
        else:
            insert_cols = [
                "UserName",
                "UserEmail",
                "UserPassword",
                "UserCity",
                "UserState",
                "UserCountry",
                "UserDateCreated",
                "UserImageURL",
            ]
            insert_values = [
                UserName,
                UserEmail,
                UserPassword,
                UserCity,
                UserState,
                UserCountry,
                UserDateCreated,
                UserImageURL,
            ]
            insert_query = """INSERT INTO {0} ({1}) VALUES {2}""".format(
                "users", ",".join(insert_cols), insert_values
            )
            cur.execute(insert_query)
            cur.close()
            conn.commit()
            conn.close()
            returnable = {"isError": False, "message": "Account successfully created"}
            return jsonify(returnable)

    # GetUserProfile
    elif request.method == "POST" and "GetUserProfile" in request.form:
        UserName = request.form["UserName"].lower()
        query = """SELECT UserName, UserImageURL, UserCity, UserState, UserZip
                    FROM users
                    WHERE UserName = {0}""".format(
            UserName
        )
        UserProfile = pd.read_sql(query, conn)
        UserImageURL = UserProfile["UserImageURL"]
        UserLocation = UserProfile[["UserCity", "UserState", "UserZip"]].values

        query = """SELECT InventoryID, TreeHistoryAction, TreeHistoryActionDate
                    FROM trees_history
                    WHERE UserName = {0}""".format(
            UserName
        )
        TreeUserHistory = pd.read_sql(query, conn)
        TreeList = TreeUserHistory["InventoryID"].unique()
        TreesWateredSum = len(
            TreeUserHistory[TreeUserHistory["TreeHistoryAction"] == "Watered"]
        )
        TreesPlantedSum = len(
            TreeUserHistory[TreeUserHistory["TreeHistoryAction"] == "Planted"]
        )
        TreesIdentifiedSum = len(
            TreeUserHistory[TreeUserHistory["TreeHistoryAction"] == "Identified"]
        )
        AchievementSum = TreesWateredSum + TreesPlantedSum + TreesIdentifiedSum
        UserTreeList = [
            UserImageURL,
            UserName,
            AchievementSum,
            TreesWateredSum,
            TreesPlantedSum,
            TreesIdentifiedSum,
            TreeList,
        ]
        returnable = {
            "isError": False,
            "UserLocation": UserLocation,
            "UserTreeList": UserTreeList,
        }
        return jsonify(returnable)

    # InviteFriend
    elif request.method == "GET" and "InviteFriend" in request.form:
        # Not sure of what the functionality should be for API here
        returnable = {"isError": True, "message": "not implemented"}
        return jsonify(returnable)
    else:
        returnable = {"isError": False, "Message": "Welcome!"}
        return jsonify(returnable)


@app.route("/tree", methods=["POST", "GET"])
def tree():
    conn = get_conn()
    cur = conn.cursor()
    # CreateTree
    if request.method == "POST" and "CreateTree" in request.form:
        TreeStatus = request.form["TreeStatus"]
        TreeName = request.form["TreeName"]
        CommonName = request.form["CommonName"]
        BotanicalName = request.form["BotanicalName"]
        Longitude = request.form["Longitude"]
        Latitude = request.form["Latitude"]
        Address = request.form["Address"]
        Street = request.form["Street"]
        TreeCity = request.form["tree_city"]
        TreeState = request.form["tree_state"]
        TreeCountry = request.form["tree_country"]
        TreeZip = request.form["tree_zip"]
        TreeWaterLevel = request.form["tree_water_level"]
        TreeHealth = request.form["tree_health"]
        TreeInsects = request.form["tree_insects"]
        TreeBroken = request.form["tree_broken"]
        TreePlantDate = request.form["tree_plant_date"]
        SelecTreeLink = request.form["SelecTreeLink"]
        create_cols = [
            "TreeStatus",
            "TreeName",
            "CommonName",
            "BotanicalName",
            "Longitude",
            "Latitude",
            "Address",
            "Street",
            "TreeCity",
            "TreeState",
            "TreeCountry",
            "TreeZip",
            "TreeWaterLevel",
            "TreeHealth",
            "TreeInsects",
            "TreeBroken",
            "TreePlantDate",
            "SelecTreeLink",
        ]
        create_values = [
            TreeStatus,
            TreeName,
            CommonName,
            BotanicalName,
            Longitude,
            Latitude,
            Address,
            Street,
            TreeCity,
            TreeState,
            TreeCountry,
            TreeZip,
            TreeWaterLevel,
            TreeHealth,
            TreeInsects,
            TreeBroken,
            TreePlantDate,
            SelecTreeLink,
        ]
        create_query = """INSERT INTO {0} ({1}) VALUES {2}""".format(
            "trees_inventory", ",".join(create_cols), create_values
        )
        cur.execute(create_query)
        cur.close()
        conn.commit()
        conn.close()
        returnable = {"isError": False, "message": "Tree successfully created"}
        return jsonify(returnable)
    # ActionTree
    elif request.method == "POST" and "ActionTree" in request.form:
        InventoryID = request.form["InventoryID"]
        UserID = request.form["UserID"]
        action_cols = ["InventoryID", "UserID", "TreeHistoryAction"]
        action_values = [InventoryID, UserID, "Identified"]
        action_query = """INSERT INTO {0} ({1}) VALUES {2}""".format(
            "trees_history", ",".join(action_cols), action_values
        )
        cur.execute(action_query)
        cur.close()
        conn.commit()
        conn.close()
        returnable = {"isError": False, "message": "Tree action successfully created"}
        return jsonify(returnable)

    # PostTree
    elif request.method == "POST" and "PostTree" in request.form:
        InventoryID = request.form["InventoryID"]
        TreeStatus = request.form["TreeStatus"]
        TreeName = request.form["TreeName"]
        CommonName = request.form["CommonName"]
        BotanicalName = request.form["BotanicalName"]
        Longitude = request.form["Longitude"]
        Latitude = request.form["Latitude"]
        Address = request.form["Address"]
        Street = request.form["Street"]
        TreeCity = request.form["tree_city"]
        TreeState = request.form["tree_state"]
        TreeCountry = request.form["tree_country"]
        TreeZip = request.form["tree_zip"]
        TreeWaterLevel = request.form["tree_water_level"]
        TreeHealth = request.form["tree_health"]
        TreeInsects = request.form["tree_insects"]
        TreeBroken = request.form["tree_broken"]
        TreePlantDate = request.form["tree_plant_date"]
        SelecTreeLink = request.form["SelecTreeLink"]
        UserID = request.form["user_id"]
        query = "SELECT user_id FROM users WHERE user_id = {}".format(UserID)
        UserCheck = pd.read_sql(query, conn)
        if len(UserCheck) == 0:
            returnable = {"isError": True, "message": "Login to update tree"}
            return jsonify(returnable)
        query = "SELECT InventoryID FROM trees_inventory WHERE InventoryID={}".format(
            InventoryID
        )
        TreeCheck = pd.read_sql(query, conn)
        if len(TreeCheck) > 0:
            update_cols = [
                "InventoryID",
                "TreeStatus",
                "TreeName",
                "CommonName",
                "BotanicalName",
                "Longitude",
                "Latitude",
                "Address",
                "Street",
                "TreeCity",
                "TreeState",
                "TreeCountry",
                "TreeZip",
                "TreeWaterLevel",
                "TreeHealth",
                "TreeInsects",
                "TreeBroken",
                "TreePlantDate",
                "SelecTreeLink",
            ]
            update_values = [
                InventoryID,
                TreeStatus,
                TreeName,
                CommonName,
                BotanicalName,
                Longitude,
                Latitude,
                Address,
                Street,
                TreeCity,
                TreeState,
                TreeCountry,
                TreeZip,
                TreeWaterLevel,
                TreeHealth,
                TreeInsects,
                TreeBroken,
                TreePlantDate,
                SelecTreeLink,
            ]
            update_query = """UPDATE trees_inventory
                            SET {0} VALUES ({1})""".format(
                ",".join(update_cols), update_values
            )
            cur.execute(update_query)
            cur.close()
            conn.commit()
            conn.close()
            returnable = {"isError": False, "message": "Tree successfully updated"}
            return returnable
        else:
            returnable = {"isError": True, "message": "Tree must be created"}
            return jsonify(returnable)

    # GetTreeList
    if request.method == "GET" and "GetTreeList" in request.form:
        query = """SELECT DISTINCT CommonName
                   FROM trees_inventory"""
        TreeList = pd.read_sql(query, conn)
        TreeList = TreeList.values
        if len(TreeList) == 0:
            returnable = {"isError": False, "message": "No unique tree common names"}
            return jsonify(returnable)
        else:
            returnable = {"isError": False, "TreeList": TreeList}
            return jsonify(returnable)

    # GetTree
    if request.method == "GET" and "GetTree" in request.form:
        InventoryID = request.form["InventoryID"]
        query = """SELECT * FROM trees_inventory
                WHERE InventoryID = {0}""".format(
            InventoryID
        )
        TreeRecord = pd.read_sql(query, conn)
        TreeRecord = TreeRecord.values
        if len(TreeRecord) == 0:
            returnable = {"isError": True, "message": "Tree does not exist"}
            return jsonify(returnable)
        returnable = {"isError": False, "TreeRecord": TreeRecord}
        return jsonify(returnable)

    # GetTreeHistory
    if request.method == "GET" and "GetTreeHistory" in request.form:
        InventoryID = request.form["InventoryID"]
        query = """SELECT tree_history_action, tree_history_action_date
                FROM trees_history
                WHERE InventoryID = {0}""".format(
            InventoryID
        )
        TreeHistory = pd.read_sql(query, conn)
        if len(TreeHistory) == 0:
            return jsonify(isError=True, message="Tree has no history")
        else:
            TreeHistory = TreeHistory.sort_values("tree_history_action_date")
            TreeHistory = TreeHistory.values
            returnable = {"isError": True, "TreeHistory": TreeHistory}
            return json.dumps(returnable)

    if request.method == "GET" and "GetMap" in request.args.get("requestType"):
        sw = request.args.get("sw")
        ne = request.args.get("ne")
        query = """SELECT * FROM trees_inventory
        WHERE Latitude >= {0}
        AND Latitude <= {1}
        AND Longitude >= {2}
        AND Longitude <= {3}""".format(
            sw[0], ne[0], sw[1], ne[1]
        )
        TreeMap = pd.read_sql(query, conn)
        if len(TreeMap) == 0:
            returnable = {"isError": True, "message": "No Trees"}
            return json.dumps(returnable)
        else:
            returnable = {"isError": False, "TreeMap": TreeMap.values}
            return jsonify(returnable)
    else:
        returnable = {"isError": True, "statusCode": 400}
        return jsonify(returnable)


if __name__ == "__main__":
    app.run(port=30000, debug=True)
