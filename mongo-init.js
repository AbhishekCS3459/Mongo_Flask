db = db.getSiblingDB("admin");


db.createUser({
  user: "admin",
  pwd: "admin_password",
  roles: [{ role: "root", db: "admin" }]
});

db = db.getSiblingDB("database_a");
db.createCollection("collection_a");

db = db.getSiblingDB("database_b");
db.createCollection("collection_b");

db = db.getSiblingDB("database_c");
db.createCollection("collection_c");
