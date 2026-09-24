import os
import sqlite3

from flask import Flask, request

app = Flask(__name__)


# 1. SQL injection: user input is inserted directly into SQL.
@app.route("/users")
def users():
    username = request.args.get("username", "")

    with sqlite3.connect("demo.db") as connection:
        query = (
            "SELECT username FROM users "
            "WHERE username = '" + username + "'"
        )
        rows = connection.execute(query).fetchall()

    return {"users": rows}


# 2. Command injection: user input reaches a shell command.
@app.route("/lookup")
def lookup():
    hostname = request.args.get("hostname", "")
    return os.popen("nslookup " + hostname).read()


# 3. Path traversal: user input controls which file is read.
@app.route("/download")
def download():
    import os
import sqlite3

from flask import Flask, request

app = Flask(__name__)


# 1. SQL injection: user input is inserted directly into SQL.
@app.route("/users")
def users():
    username = request.args.get("username", "")

    with sqlite3.connect("demo.db") as connection:
        query = (
            "SELECT username FROM users "
            "WHERE username = '" + username + "'"
        )
        rows = connection.execute(query).fetchall()

    return {"users": rows}


# 2. Command injection: user input reaches a shell command.
@app.route("/lookup")
def lookup():
    hostname = request.args.get("hostname", "")
    return os.popen("nslookup " + hostname).read()


# 3. Path traversal: user input controls which file is read.
@app.route("/download")
def download():
    filename = request.args.get("filename", "")
    with open("documents/" + filename, encoding="utf-8") as file:
        return file.read()
    filename = request.args.get("filename", "")
    with open("documents/" + filename, encoding="utf-8") as file:
        return file.read()
