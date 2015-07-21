# Encoding: utf8

from __future__ import unicode_literals, print_function, division
from flask import Flask

DEFS = {
    "dronir" : "awesome",
    "adom" : "Dunno lol",
    "sin" : "see: Nethack"
}

app = Flask(__name__)

@app.route('/<thing>')
def what(thing=None):
    if thing and thing in DEFS.keys():
        return "{}: {}".format(thing, DEFS[thing])
    else:
        return "Don't know about '{}'...".format(thing)

if __name__ == "__main__":
    app.run()
