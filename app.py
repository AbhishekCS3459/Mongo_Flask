from flask import Flask, request, jsonify
from pymongo import MongoClient
from flask_jwt_extended import create_access_token, jwt_required, JWTManager, get_jwt_identity
import json

app = Flask(__name__)

# JWT Secret Key
app.config["JWT_SECRET_KEY"] = "your_jwt_secret"
jwt = JWTManager(app)

# MongoDB Connection (Admin User)
ADMIN_USER = "admin"
ADMIN_PASS = "adminpassword"

def get_db(user, password, dbname):
    uri = f"mongodb://{user}:{password}@localhost:27017/{dbname}?authSource=admin"
    client = MongoClient(uri)
    return client[dbname]

# Mock user credentials (to be stored securely)
users = {
    "admin": {"password": ADMIN_PASS, "db": "admin", "role": "admin"},
    "user_x": {"password": "password_x", "db": "database_a", "role": "user"},
    "user_y": {"password": "password_y", "db": "database_b", "role": "user"},
    "user_z": {"password": "password_z", "db": "database_c", "role": "user"},
}

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if username in users and users[username]["password"] == password:
        token = create_access_token(identity=json.dumps({"username": username, "db": users[username]["db"], "role": users[username]["role"]}))
        return jsonify({"token": token}), 200
    return jsonify({"error": "Invalid credentials"}), 401

@app.route("/assign-role", methods=["POST"])
@jwt_required()
def assign_role():
    identity = json.loads(get_jwt_identity())  
    if identity["role"] != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    data = request.json
    new_user = data.get("username")
    password = data.get("password")
    db_name = data.get("db")
    role = data.get("role", "readWrite")  

    if not (new_user and password and db_name):
        return jsonify({"error": "username, password, and db are required"}), 400

    client = MongoClient(f"mongodb://{ADMIN_USER}:{ADMIN_PASS}@localhost:27017/admin?authSource=admin")
    admin_db = client["admin"]
    
    try:
        admin_db.command("createUser", new_user, pwd=password, roles=[{"role": role, "db": db_name}])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    users[new_user] = {"password": password, "db": db_name, "role": "user"} 
    return jsonify({
        "message": "User role assigned successfully",
        "data": f"{new_user} is assigned {role}"
    }), 201

@app.route("/insert", methods=["POST"])
@jwt_required()
def insert_data():
    identity = json.loads(get_jwt_identity())  
    dbname = identity["db"]
    username = identity["username"]

    db = get_db(username, users[username]["password"], dbname)
    collection_name = request.json.get("collection")
    data = request.json.get("data")

    if not collection_name or not data:
        return jsonify({"error": "Collection and data required"}), 400

    collection = db[collection_name]
    result = collection.insert_one(data)
    return jsonify({"message": "Data inserted", "id": str(result.inserted_id)}), 201


@app.route("/get-users", methods=["GET"])
@jwt_required()
def get_users():
    identity = json.loads(get_jwt_identity()) 
    if identity["role"] != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    users_list = [{"username": user, "db": users[user]["db"], "role": users[user]["role"]} for user in users]
    return jsonify({"users": users_list}), 200


@app.route("/test", methods=["GET"])
def test():
    return jsonify({"message": "Flask app is running successfully!"}), 200

if __name__ == "__main__":
    app.run(debug=True)
