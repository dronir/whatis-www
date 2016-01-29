# Encoding: utf8

from __future__ import unicode_literals, print_function, division
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, flash
from flask import render_template
from contextlib import closing

app = Flask(__name__)
app.config.from_object("config")


# Database handling functions

def connect_db():
    """Connect to the database and return handle."""
    return sqlite3.connect(app.config['DATABASE'])

def get_db():
    """Return the database handle, connecting to it if necessary."""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = connect_db()
    return db

def init_db():
    """Initialize an empty database (handle with care!)."""
    with closing(connect_db()) as db, app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
        db.commit()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


# Definition handling functions

def format_entries(fetch):
    return [{"key" : row[1],
            "definition" : row[2],
            "definer" : row[3],
            "timestamp" : row[4]}
        for row in fetch]

# WHATIS
@app.route("/whatis/<thing>")
def show_definition(thing=None):
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    cursor = get_db().execute("select * from entries where key = ?", [thing])
    entries = format_entries(cursor.fetchall())
    return render_template("definitions.html", entries=entries, thing=thing)


# DEFINE
@app.route("/define/<thing>/<what>")
def define(thing=None, what=None):
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    if not session.get("admin_rights"):
        flash("You're not allowed to define.")
        return redirect("/whatis/{}".format(thing))
    if not thing and what:
        return ""
    get_db().execute("insert into entries (key, definition, definer) values (?, ?, ?)",
        [thing, what, "dronir"])
    get_db().commit()
    flash("Definition added.")
    return redirect("/whatis/{}".format(thing))


@app.route("/")
def root():
    return redirect("/list/all")

@app.route("/list/")
def emptylist():
    return redirect("/list/all")

def listquery(query):
    cursor = get_db().execute(query)
    return [x[0] for x in cursor.fetchall()]

@app.route("/list/<letter>")
def listing(letter=None):
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    items = []
    if letter.lower() == "all":
        items = listquery("select distinct key from entries")
    elif letter.lower() in "abcdefghijklmnopqrstuvwxyz0123456789":
        items = listquery(
                "select distinct key from entries where key glob '[{}{}]*'".format(
                letter.upper(), letter.lower()))
    elif letter.lower() == "0-9":
        items = listquery("select distinct key from entries where key glob '[0-9]*'")
    elif letter.lower() == "other":
        items = listquery("select distinct key from entries where key glob '[^A-Za-z0-9]*'")
    items.sort(key=unicode.lower)
    return render_template("list.html", items=items, letter=letter)


# Login and logout functions

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "GET" and session.get("logged_in"):
        flash("Already logged in.")
        return redirect("/list/all")
    if request.method == "POST":
        if request.form['usertype'] == "user":
            if request.form['password'] != app.config['PASSWORD']:
                error = "Invalid password"
            else:
                session["logged_in"] = True
            return redirect("/list/all")
        elif request.form['usertype'] == "admin":
            if request.form['password'] != app.config['ADMIN_PASSWORD']:
                error = "Invalid password"
            else:
                session["logged_in"] = True
                session["admin_rights"] = True
            return redirect("/list/all")
            
    return render_template("login.html", error=error)

@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    session.pop("admin_rights", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run()
