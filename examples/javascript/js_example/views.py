from flask import jsonify
from flask import render_template
from flask import request

from js_example import app

from js_example.reference.src.main.python.similar import *


@app.route("/", defaults={"js": "plain"})
@app.route("/<any(plain, jquery, fetch):js>")
def index(js):
    return render_template(f"{js}.html", js=js)


@app.route("/add", methods=["POST"])
def add():
    print("in add function")
    query_code = request.form.get("a", "7", type=str)
    print("query code = ", query_code)
    # b = request.form.get("b", 0, type=float)
    code_recommended = get_recommended_code(query_code)
    print("add - code_recommended ", code_recommended)
    jsonify_code = jsonify(result = code_recommended)
    print("add - jsonify_code ", jsonify_code)
    return jsonify_code
