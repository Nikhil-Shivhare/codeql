"""
Advanced CodeQL Bypass Learning Lab
------------------------------------

This file contains multiple vulnerable patterns.
Each section demonstrates techniques that MAY bypass
basic or poorly configured static analysis rules.

⚠️ This is intentionally vulnerable code.
⚠️ Use only for learning.
"""

from flask import Flask, request
import os
import sqlite3
import base64

app = Flask(__name__)


# =========================================================
# 1️⃣ BASIC SQL INJECTION (SHOULD BE DETECTED)
# =========================================================

@app.route("/basic_sql")
def basic_sql():
    user_input = request.args.get("id")

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    # ❌ Direct concatenation (easy detection)
    query = "SELECT * FROM users WHERE id=" + user_input
    cursor.execute(query)

    return "Basic SQL executed"


# =========================================================
# 2️⃣ INDIRECT FUNCTION FLOW (May confuse weak rules)
# =========================================================

def build_query(user_id):
    # Vulnerable but hidden inside function
    return "SELECT * FROM users WHERE id=" + user_id

@app.route("/indirect_sql")
def indirect_sql():
    user_input = request.args.get("id")

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    # ⚠️ Data flow goes through custom function
    query = build_query(user_input)
    cursor.execute(query)

    return "Indirect SQL executed"


# =========================================================
# 3️⃣ BASE64 TRANSFORMATION LAYER
# =========================================================

@app.route("/encoded_sql")
def encoded_sql():
    encoded = request.args.get("id")

    # ⚠️ Transformation layer
    decoded = base64.b64decode(encoded).decode()

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    query = "SELECT * FROM users WHERE id=" + decoded
    cursor.execute(query)

    return "Encoded SQL executed"


# =========================================================
# 4️⃣ OBJECT WRAPPER FLOW
# =========================================================

class Wrapper:
    def __init__(self, data):
        self.data = data

    def get_value(self):
        return self.data

@app.route("/object_sql")
def object_sql():
    wrapped = Wrapper(request.args.get("id"))

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    # ⚠️ Taint flows through object + method
    query = "SELECT * FROM users WHERE id=" + wrapped.get_value()
    cursor.execute(query)

    return "Object SQL executed"


# =========================================================
# 5️⃣ STRING JOIN METHOD
# =========================================================

@app.route("/join_sql")
def join_sql():
    user_input = request.args.get("id")

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    # ⚠️ Using join instead of +
    query = "".join(["SELECT * FROM users WHERE id=", user_input])
    cursor.execute(query)

    return "Join SQL executed"


# =========================================================
# 6️⃣ FAKE SANITIZER CONFUSION
# =========================================================

def fake_clean(data):
    # ⚠️ Looks like sanitizer but does nothing
    return data

@app.route("/fake_sanitizer")
def fake_sanitizer():
    user_input = request.args.get("id")
    safe_input = fake_clean(user_input)

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    query = "SELECT * FROM users WHERE id=" + safe_input
    cursor.execute(query)

    return "Fake sanitized SQL executed"


# =========================================================
# 7️⃣ BASIC COMMAND INJECTION (SHOULD BE DETECTED)
# =========================================================

@app.route("/basic_cmd")
def basic_cmd():
    ip = request.args.get("ip")

    # ❌ Direct command injection
    os.system("ping -c 1 " + ip)

    return "Basic command executed"


# =========================================================
# 8️⃣ EXEC() WRAPPED COMMAND
# =========================================================

@app.route("/exec_cmd")
def exec_cmd():
    ip = request.args.get("ip")

    command = "os.system('ping -c 1 " + ip + "')"

    # ⚠️ Dynamic execution
    exec(command)

    return "Exec command executed"


# =========================================================
# 9️⃣ SPLIT VARIABLE BUILDING
# =========================================================

@app.route("/split_sql")
def split_sql():
    part1 = "SELECT * FROM users WHERE id="
    part2 = request.args.get("id")

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    # ⚠️ Flow split into parts
    query = part1 + part2
    cursor.execute(query)

    return "Split SQL executed"


# =========================================================
# 1️⃣0️⃣ INDIRECT GLOBAL VARIABLE FLOW
# =========================================================

GLOBAL_VAR = None

@app.route("/global_flow")
def global_flow():
    global GLOBAL_VAR
    GLOBAL_VAR = request.args.get("id")

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    query = "SELECT * FROM users WHERE id=" + GLOBAL_VAR
    cursor.execute(query)

    return "Global flow SQL executed"


# =========================================================

if __name__ == "__main__":
    app.run(debug=True)