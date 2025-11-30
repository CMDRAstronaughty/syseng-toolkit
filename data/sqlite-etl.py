import sqlite3

db_path = "/home/myintsai/Documents/syseng-toolkit/data/systems_of_systems.db"
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# --------------------------
# Drop existing tables
# --------------------------
tables = [
    "requirement_verification",
    "verification_method",
    "requirement",
    "system"
]

for t in tables:
    cur.execute(f"DROP TABLE IF EXISTS {t}")

# --------------------------
# Create SYSTEM table
# --------------------------
cur.execute("""
CREATE TABLE system (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);
""")

# --------------------------
# Create REQUIREMENT table
# --------------------------
cur.execute("""
CREATE TABLE requirement (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    system_id INTEGER,
    parent_requirement_id INTEGER,
    level TEXT CHECK(level IN ('system','functional')) NOT NULL,
    description TEXT NOT NULL,
    owner TEXT,
    planned_closure_date TEXT,
    actual_closure_date TEXT,
    
    FOREIGN KEY(system_id) REFERENCES system(id),
    FOREIGN KEY(parent_requirement_id) REFERENCES requirement(id)
);
""")

# --------------------------
# Verification Methods Table
# --------------------------
cur.execute("""
CREATE TABLE verification_method (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);
""")

# --------------------------
# Requirement ↔ Verification Method (M:N)
# --------------------------
cur.execute("""
CREATE TABLE requirement_verification (
    requirement_id INTEGER,
    verification_method_id INTEGER,
    PRIMARY KEY(requirement_id, verification_method_id),
    
    FOREIGN KEY(requirement_id) REFERENCES requirement(id),
    FOREIGN KEY(verification_method_id) REFERENCES verification_method(id)
);
""")

# --------------------------
# Populate Verification Methods
# --------------------------
methods = ["demonstration", "inspection", "analysis"]
cur.executemany(
    "INSERT INTO verification_method(name) VALUES (?)",
    [(m,) for m in methods]
)

conn.commit()
conn.close()

print("Database created:", db_path)
