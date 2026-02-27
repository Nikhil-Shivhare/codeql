"""
Advanced CodeQL Evasion & Static Analysis Challenge Lab

⚠️ This file contains intentionally vulnerable patterns.
⚠️ Use for learning only (not production).

This file introduces more sophisticated patterns that can 
confuse static analysis engines — such as:
- dynamic attribute invocation
- reflection
- higher-order taint propagation
- indirect control / data flows
- deferred evaluation
"""

from flask import Flask, request
import sqlite3
import os
import base64
import importlib

app = Flask(__name__)

# -----------------------------------------------------------
# 1) DYNAMIC IMPORT & EXECUTION
# -----------------------------------------------------------

@app.route("/dynamic_import")
def dynamic_import():
    # Attacker controls module and function name
    mod_name = request.args.get("m")
    fn_name = request.args.get("f")

    # Dynamically import module at runtime
    mod = importlib.import_module(mod_name)

    # Dynamically get function
    func = getattr(mod, fn_name)

    # DIRECT EXECUTION WITH UNTRUSTED DATA
    return func(request.args.get("p"))  # potential RCE


# -----------------------------------------------------------
# 2) REFLECTIVE ATTRIBUTE INVOCATION
# -----------------------------------------------------------

@app.route("/reflective_call")
def reflective_call():
    ip = request.args.get("ip")

    cmd_obj = os  # system module reference
    method_name = "system"  # method name as string

    # Use getattr to call os.system
    method = getattr(cmd_obj, method_name)
    method("ping -c 1 " + ip)

    return "reflective ping"


# -----------------------------------------------------------
# 3) TAINT VIA DEFERRED EVALUATION (LAMBDA)
# -----------------------------------------------------------

@app.route("/lambda_sql")
def lambda_sql():
    user_input = request.args.get("id")

    # Create lambda with unsafe execution
    exec_sql = lambda x: "SELECT * FROM users WHERE id=" + x

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute(exec_sql(user_input))

    return "lambda SQL"


# -----------------------------------------------------------
# 4) NESTED STRUCTURES WITH LIST COMPREHENSIONS
# -----------------------------------------------------------

@app.route("/nested_flow")
def nested_flow():
    vals = [request.args.get("id"), "safe"]

    # nested list comprehension obscures flow
    query_parts = [f"SELECT * FROM users WHERE id={v}" for v in vals]
    query = " UNION ".join(query_parts)

    conn = sqlite3.connect("users.db")
    cur = conn.cursor()
    cur.execute(query)

    return "nested flow executed"


# -----------------------------------------------------------
# 5) TYPED DECORATOR THAT PROPAGATES TAINT
# -----------------------------------------------------------

def taint_decorator(fn):
    def wrapper(x):
        # wrapper doesn't sanitize
        return fn(x)
    return wrapper

@taint_decorator
def unsafe_query(x):
    return "SELECT * FROM users WHERE id=" + x

@app.route("/decorator_sql")
def decorator_sql():
    inp = request.args.get("id")
    c = sqlite3.connect("users.db").cursor()
    c.execute(unsafe_query(inp))
    return "decorated SQL"


# -----------------------------------------------------------
# 6) CONTROLLED INDIRECT CONCATENATION
# -----------------------------------------------------------

@app.route("/indirect_concat")
def indirect_concat():
    p1 = "SELECT "
    p2 = " * FROM users WHERE id="
    user = request.args.get("id")

    # combine parts indirectly
    query = "".join([p1, p2, str(user)])
    sqlite3.connect("users.db").cursor().execute(query)
    return "indirect concat"


# -----------------------------------------------------------
# 7) VARIABLE TYPE CONFUSION (CASTS + BUILTINS)
# -----------------------------------------------------------

@app.route("/type_confusion")
def type_confusion():
    val = request.args.get("id")
    # convert to int (could crash)
    try:
        ival = int(val)
    except:
        ival = 0
    q = "SELECT * FROM users WHERE id =" + str(ival)
    sqlite3.connect("users.db").cursor().execute(q)
    return "type confusion"


# -----------------------------------------------------------
# 8) CUSTOM SANITIZER WITH NO EFFECT
# -----------------------------------------------------------

def pseudo_sanitize(x):
    # obfuscates string but not safe
    return base64.b64decode(base64.b64encode(x.encode())).decode()

@app.route("/pseudo_sanitize")
def pseudo_sanitize_sql():
    raw = request.args.get("id")
    clean = pseudo_sanitize(raw)
    q = "SELECT * FROM users WHERE id=" + clean
    sqlite3.connect("users.db").cursor().execute(q)
    return "pseudo sanitized SQL"


if __name__ == "__main__":
    app.run(debug=True)
    