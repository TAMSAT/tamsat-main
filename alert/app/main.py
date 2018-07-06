#!/usr/bin/env python3

import os
from flask import Flask, send_file, abort
app = Flask(__name__)


@app.route("/hello")
def hello():
    return "Hello World from Flask!!!!"


@app.route("/")
def main():
    index_path = os.path.join(app.static_folder, 'index.html')
    return send_file(index_path)

# Everything not declared before (not a Flask route / API endpoint)...


@app.route('/<path:path>')
def route_frontend(path):
    # ...could be a static file needed by the front end that
    # doesn't use the `static` path (like in `<script src="bundle.js">`)
    file_path = os.path.join(app.static_folder, path)
    if os.path.isfile(file_path):
        return send_file(file_path)
    # Otherwise, send 404
    else:
        abort(404)


if __name__ == "__main__":
    # Only for debugging while developing
    app.run(host='0.0.0.0', debug=True, port=8080)
