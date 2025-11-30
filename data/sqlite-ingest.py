import sqlite3

db = "/home/myintsai/Documents/syseng-toolkit/data/systems_of_systems.db"
conn = sqlite3.connect(db)
cur = conn.cursor()

# ------------------------------
# Insert Systems
# ------------------------------
systems = [
    ("Orbital Imaging System",),
    ("Autonomous Ground Vehicle",)
]

cur.executemany("INSERT INTO system(name) VALUES (?)", systems)

# Retrieve System IDs
cur.execute("SELECT id, name FROM system")
system_ids = {name: sid for sid, name in cur.fetchall()}

# ------------------------------
# Insert System-Level Requirements
# ------------------------------
system_reqs = [
    (system_ids["Orbital Imaging System"], None, "system", 
     "The spacecraft shall capture imagery at 0.5m resolution.", 
     "Alice", "2025-03-01", None),

    (system_ids["Orbital Imaging System"], None, "system",
     "The spacecraft shall store at least 1TB of imagery data.",
     "Bob", "2025-06-01", None),

    (system_ids["Autonomous Ground Vehicle"], None, "system",
     "The vehicle shall autonomously navigate paved environments.",
     "Carol", "2025-02-15", None),

    (system_ids["Autonomous Ground Vehicle"], None, "system",
     "The vehicle shall maintain obstacle avoidance within 1 meter.",
     "Dave", "2025-04-10", None),

    (system_ids["Orbital Imaging System"], None, "system",
     "The spacecraft shall transmit imagery to ground station within 24 hours.",
     "Alice", "2025-05-15", None),
]

cur.executemany("""
INSERT INTO requirement(system_id, parent_requirement_id, level, description, owner, planned_closure_date, actual_closure_date)
VALUES (?, ?, ?, ?, ?, ?, ?)
""", system_reqs)

# Fetch system-level requirement IDs
cur.execute("""
SELECT id, description FROM requirement WHERE level='system'
""")
req_ids = {desc: rid for rid, desc in cur.fetchall()}

# ------------------------------
# Insert Functional-Level Requirements
# ------------------------------

functional_reqs = [
    # Orbital Imaging System → Resolution
    (system_ids["Orbital Imaging System"], req_ids["The spacecraft shall capture imagery at 0.5m resolution."], 
     "functional", "Camera shall operate at minimum 200 megapixels.",
     "Alice", "2025-03-01", None),

    (system_ids["Orbital Imaging System"], req_ids["The spacecraft shall capture imagery at 0.5m resolution."],
     "functional", "Optics shall maintain focus across ±10°C temperature variation.",
     "Bob", "2025-03-15", None),

    # Orbital Imaging System → Storage
    (system_ids["Orbital Imaging System"], req_ids["The spacecraft shall store at least 1TB of imagery data."],
     "functional", "Storage subsystem shall provide at least 1.2TB usable capacity.",
     "Charlie", "2025-06-01", None),

    (system_ids["Orbital Imaging System"], req_ids["The spacecraft shall store at least 1TB of imagery data."],
     "functional", "Storage subsystem shall use radiation-tolerant memory.",
     "Charlie", "2025-06-10", None),

    # Orbital Imaging System → Downlink
    (system_ids["Orbital Imaging System"], req_ids["The spacecraft shall transmit imagery to ground station within 24 hours."],
     "functional", "Radio system shall support ≥ 50 Mbps downlink rate.",
     "Alice", "2025-05-15", None),

    (system_ids["Orbital Imaging System"], req_ids["The spacecraft shall transmit imagery to ground station within 24 hours."],
     "functional", "Transmission scheduler shall allocate transmission windows autonomously.",
     "Dave", "2025-05-20", None),

    # AGV → Navigation
    (system_ids["Autonomous Ground Vehicle"], req_ids["The vehicle shall autonomously navigate paved environments."],
     "functional", "Navigation stack shall localize within ±0.1m accuracy.",
     "Carol", "2025-02-15", None),

    (system_ids["Autonomous Ground Vehicle"], req_ids["The vehicle shall autonomously navigate paved environments."],
     "functional", "Lane detection algorithm shall operate reliably up to 120 km/h.",
     "Eve", "2025-03-01", None),

    # AGV → Obstacle Avoidance
    (system_ids["Autonomous Ground Vehicle"], req_ids["The vehicle shall maintain obstacle avoidance within 1 meter."],
     "functional", "LiDAR subsystem shall detect obstacles at 50 meters.",
     "Dave", "2025-04-10", None),

    (system_ids["Autonomous Ground Vehicle"], req_ids["The vehicle shall maintain obstacle avoidance within 1 meter."],
     "functional", "Vehicle controller shall apply braking within 200 ms of obstacle detection.",
     "Carol", "2025-04-15", None),
]

cur.executemany("""
INSERT INTO requirement(system_id, parent_requirement_id, level, description, owner, planned_closure_date, actual_closure_date)
VALUES (?, ?, ?, ?, ?, ?, ?)
""", functional_reqs)

# Fetch all requirements again for verification mapping
cur.execute("SELECT id, description FROM requirement")
all_reqs = {desc: rid for rid, desc in cur.fetchall()}

# ------------------------------
# Verification Methods Mapping
# ------------------------------

# Fetch method IDs
cur.execute("SELECT id, name FROM verification_method")
method_ids = {name: mid for mid, name in cur.fetchall()}

verification_mappings = [
    # System-level: resolution requirement (inspection relies on functional reqs)
    (all_reqs["The spacecraft shall capture imagery at 0.5m resolution."], method_ids["inspection"]),
    (all_reqs["The spacecraft shall capture imagery at 0.5m resolution."], method_ids["analysis"]),

    # Functional resolution children
    (all_reqs["Camera shall operate at minimum 200 megapixels."], method_ids["demonstration"]),
    (all_reqs["Optics shall maintain focus across ±10°C temperature variation."], method_ids["analysis"]),

    # Storage requirements
    (all_reqs["The spacecraft shall store at least 1TB of imagery data."], method_ids["analysis"]),
    (all_reqs["Storage subsystem shall provide at least 1.2TB usable capacity."], method_ids["demonstration"]),
    (all_reqs["Storage subsystem shall use radiation-tolerant memory."], method_ids["inspection"]),

    # Downlink
    (all_reqs["The spacecraft shall transmit imagery to ground station within 24 hours."], method_ids["analysis"]),
    (all_reqs["Radio system shall support ≥ 50 Mbps downlink rate."], method_ids["demonstration"]),
    (all_reqs["Transmission scheduler shall allocate transmission windows autonomously."], method_ids["analysis"]),

    # Navigation
    (all_reqs["The vehicle shall autonomously navigate paved environments."], method_ids["analysis"]),
    (all_reqs["Navigation stack shall localize within ±0.1m accuracy."], method_ids["analysis"]),
    (all_reqs["Lane detection algorithm shall operate reliably up to 120 km/h."], method_ids["demonstration"]),

    # Obstacle avoidance
    (all_reqs["The vehicle shall maintain obstacle avoidance within 1 meter."], method_ids["inspection"]),
    (all_reqs["LiDAR subsystem shall detect obstacles at 50 meters."], method_ids["demonstration"]),
    (all_reqs["Vehicle controller shall apply braking within 200 ms of obstacle detection."], method_ids["analysis"]),
]

cur.executemany("""
INSERT INTO requirement_verification(requirement_id, verification_method_id)
VALUES (?, ?)
""", verification_mappings)

conn.commit()
conn.close()

print("Sample data inserted.")
