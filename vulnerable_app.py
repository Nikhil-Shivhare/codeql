from flask import Flask, request
import sqlite3
import subprocess

app = Flask(__name__)


@app.route("/user")
def get_user():
    user_id = request.args.get("id")

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    # ❌ VULNERABLE: SQL Injection
    # User input directly concatenated into query
    query = "SELECT * FROM users WHERE id = " + user_id
    cursor.execute(query)

    result = cursor.fetchall()
    conn.close()

    return str(result)

@app.route("/ping")
def ping():
    ip = request.args.get("ip")

    # ❌ VULNERABLE: Command Injection
    # Directly passing user input into shell command
    import os
    os.system("ping -c 1 " + ip)

    return "Ping executed"