# Encoding: utf8

from __future__ import unicode_literals, print_function, division
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return "Lol hello."

if __name__ == "__main__":
    app.run()
