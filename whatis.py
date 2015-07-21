# Encoding: utf8

from __future__ import unicode_literals, print_function, division
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, flash
from flask import render_template
from contextlib import closing

app = Flask(__name__)
app.config.from_object("config")

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = connect_db()
    return db

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


def format_entries(fetch):
    return [{"key" : row[1],
            "definition" : row[2],
            "definer" : row[3],
            "timestamp" : row[4]}
        for row in fetch]

@app.route("/whatis/<thing>")
def show_definition(thing=None):
    #if not session.get("logged_in"):
    #    abort(401)
    cur = get_db().execute("select * from entries where key = ?", [thing])
    entry = format_entries(cur.fetchall())
    print(entry)
    return ""

@app.route("/define/<thing>/<what>")
def define(thing=None, what=None):
    if not thing and what:
        return ""
    get_db().execute("insert into entries (key, definition, definer) values (?, ?, ?)",
        [thing, what, "dronir"])
    get_db().commit()
    flash("Defined {} as {}".format(thing, what))
    return ""
        

if __name__ == "__main__":
    app.run(debug=True)
