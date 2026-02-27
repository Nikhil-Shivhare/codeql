"""
Super Advanced CodeQL Evasion Lab
--------------------------------

This file uses highly dynamic constructs and indirect control/data
flows that are challenging for static analysis engines to model.

⚠️ Not safe for production — for learning only!
"""

from flask import Flask, request
import sqlite3
import os
import base64
import importlib

app = Flask(__name__)

# --------------------------------------------------------
# 1) DYNAMICALLY GENERATED CODE + EVAL
# --------------------------------------------------------

@app.route("/dynamic_eval_sql")
def dynamic_eval_sql():
    # Build code at runtime
    template = "q='SELECT * FROM users WHERE id=' + user_in"
    user_in = request.args.get("id")
    exec(template)  # Runtime code generation
    conn = sqlite3.connect("users.db")
    cur = conn.cursor()
    return str(cur.execute(q).fetchall())


# --------------------------------------------------------
# 2) EVAL WITH CUSTOM BUILTINS
# --------------------------------------------------------

@app.route("/eval_builtins")
def eval_builtins():
    # Remove safe builtins and explicitly eval
    user_code = "cursor.execute('SELECT * FROM users WHERE id=' + " + repr(request.args.get("id")) + ")"
    namespace = {"cursor": sqlite3.connect("users.db").cursor()}
    eval(user_code, {"__builtins__": {}}, namespace)
    return "eval builtins done"


# --------------------------------------------------------
# 3) SINK INVOKED VIA REFLECTIVE WRAPPER
# --------------------------------------------------------

class ReflectiveSink:
    def __init__(self, obj):
        self._obj = obj

    def __getattr__(self, name):
        # Any attribute access becomes a call to the object
        def inner(*args, **kwargs):
            return getattr(self._obj, name)(*args, **kwargs)
        return inner

@app.route("/reflective_wrapper")
def reflective_wrapper():
    cur = ReflectiveSink(sqlite3.connect("users.db").cursor())
    val = request.args.get("id")
    # Still SQL injection, but through runtime reflection
    return str(cur.execute(f"SELECT * FROM users WHERE id={val}").fetchall())


# --------------------------------------------------------
# 4) META-PROGRAMMING WITH COMPILE()
# --------------------------------------------------------

@app.route("/compile_exec")
def compile_exec():
    raw = request.args.get("id")
    code = compile("result = 'Fetched: ' + raw", "<string>", "exec")
    loc = {"raw": raw}
    exec(code, loc)
    return loc["result"]


# --------------------------------------------------------
# 5) CUSTOM REFLECTIVE COMMAND SINK
# --------------------------------------------------------

def run_command(cmd):
    os.system(cmd)

@app.route("/indirect_cmd")
def indirect_cmd():
    # Call through intermediate function name stored in user data
    func_name = request.args.get("fn")
    command = "ping -c 1 " + request.args.get("ip")
    globals()[func_name](command)
    return "indirect cmd"


if __name__ == "__main__":
    app.run(debug=True)