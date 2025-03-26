from flask import Flask, request, jsonify
from pymongo import MongoClient
from flask_jwt_extended import create_access_token, jwt_required, JWTManager, get_jwt_identity
import json

app = Flask(__name__)

# JWT Secret Key
app.config["JWT_SECRET_KEY"] = "your_jwt_secret"
jwt = JWTManager(app)

# MongoDB Connections (with authentication)
def get_db(user, password, dbname):
    uri = f"mongodb://{user}:{password}@localhost:27017/{dbname}?authSource=admin"
    client = MongoClient(uri)
    return client[dbname]

# Mock user credentials (this should be stored securely)
users = {
    "user_x": {"password": "password_x", "db": "database_a"},
    "user_y": {"password": "password_y", "db": "database_b"},
    "user_z": {"password": "password_z", "db": "database_c"},
}

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if username in users and users[username]["password"] == password:
        token = create_access_token(identity=json.dumps({"username": username, "db": users[username]["db"]}))
        return jsonify({"token": token}), 200
    return jsonify({"error": "Invalid credentials"}), 401

@app.route("/insert", methods=["POST"])
@jwt_required()
def insert_data():
    identity = json.loads(get_jwt_identity())  # Decode back to dictionary
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

@app.route("/test", methods=["GET"])
def test():
    return jsonify({"message": "Flask app is running successfully!"}), 200

if __name__ == "__main__":
    app.run(debug=True)
