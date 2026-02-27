from flask import Flask, request
import sqlite3
import subprocess

app = Flask(__name__)

# ------------------------------
# SECURE VERSION (NO VULNERABILITIES)
# ------------------------------

@app.route("/user")
def get_user():
    user_id = request.args.get("id")

    # Proper DB connection
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    # ✅ SECURE: Using parameterized query
    # This prevents SQL injection
    query = "SELECT * FROM users WHERE id = ?"
    cursor.execute(query, (user_id,))

    result = cursor.fetchall()
    conn.close()

    return str(result)


@app.route("/ping")
def ping():
    ip = request.args.get("ip")

    # ✅ SECURE: Using subprocess safely (no shell=True)
    # Passing arguments as list prevents command injection
    subprocess.run(["ping", "-c", "1", ip], check=True)

    return "Ping executed safely"


if __name__ == "__main__":
    app.run(debug=True)