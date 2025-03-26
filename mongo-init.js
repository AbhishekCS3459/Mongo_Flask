db = db.getSiblingDB("admin");

// Create User X (Only Access `database_a`)
db.createUser({
  user: "user_x",
  pwd: "password_x",
  roles: [{ role: "readWrite", db: "database_a" }]
});

// Create User Y (Only Access `database_b`)
db.createUser({
  user: "user_y",
  pwd: "password_y",
  roles: [{ role: "readWrite", db: "database_b" }]
});

// Create User Z (Only Access `database_c`)
db.createUser({
  user: "user_z",
  pwd: "password_z",
  roles: [{ role: "readWrite", db: "database_c" }]
});

// Create Collections in their Databases
db = db.getSiblingDB("database_a");
db.createCollection("collection_a");

db = db.getSiblingDB("database_b");
db.createCollection("collection_b");

db = db.getSiblingDB("database_c");
db.createCollection("collection_c");
