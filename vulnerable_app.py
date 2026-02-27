from flask import Flask, request
import sqlite3
import subprocess

app = Flask(__name__)


@app.route("/user")
def get_user():
    user_id = request.args.get("id")

    # 🟢 Optional: Validate input type
    # Ensures attacker cannot inject SQL keywords easily
    if not user_id or not user_id.isdigit():
        return "Invalid ID", 400

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    # ✅ FIX 1: Parameterized Query
    # Instead of concatenation, we use placeholder (?)
    # SQLite safely escapes user input
    query = "SELECT * FROM users WHERE id = ?"
    cursor.execute(query, (user_id,))

    result = cursor.fetchall()
    conn.close()

    return str(result)


@app.route("/ping")
def ping():
    ip = request.args.get("ip")

    if not ip:
        return "Invalid IP", 400

    # ✅ FIX 2: Use subprocess without shell=True
    # Arguments passed as list
    # No shell interpretation
    # Even if attacker sends:
    # 8.8.8.8; rm -rf /
    # It will be treated as plain argument, NOT executed
    subprocess.run(["ping", "-c", "1", ip], check=True)

    return "Ping executed safely"


@app.route("/search")
def search():
    name = request.args.get("name")

    # Developer thinks this is safe
    name = name.replace("'", "")

    query = "SELECT * FROM users WHERE name = '" + name + "'"
    cursor = sqlite3.connect("users.db").cursor()
    cursor.execute(query)

    return "Done"

if __name__ == "__main__":
    # ✅ FIX 3: Disable debug mode in production
    # Debug=True exposes stack traces and sensitive info
    app.run(debug=False)
    
    
    