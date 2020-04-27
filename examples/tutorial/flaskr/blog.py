from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

from flaskr.codesearch.src.predict import *

import os
from dpu_utils.utils import RichPath
from flaskr.codesearch.src import model_restore_helper

bp = Blueprint("blog", __name__)

import sys
sys.path.insert(0, "E:\\Projects\\Flask\\my_flask_apps\\my_csn_app\\examples\\tutorial\\flaskr\\codesearch\\src\\utils")
sys.path.insert(1, "E:\\Projects\\Flask\\my_flask_apps\\my_csn_app\\examples\\tutorial\\flaskr\\codesearch\\src")
print("the syspath is added till dpu_utils")
print(sys.path)

dir_resources = os.getcwd()+"\\flaskr\\codesearch\\resources\\"
#local_model_path = dir_resources + "saved_models\\rnn-2020-04-15-06-22-47_model_best.pkl.gz"
local_model_path = dir_resources + "saved_models\\neuralbowmodel-2020-04-11-00-02-37_model_best.pkl.gz"
model_path = RichPath.create(local_model_path, None)
print("Restoring model from %s" % model_path)
#model = model_restore_helper.restore(path=model_path, is_train=False, hyper_overrides={})

@bp.route("/", methods=("GET", "POST"))
def index():
    """Show all the posts, most recent first."""
    print("in blog index")
    if request.method == "POST":
        search_query = request.form["title"]
        #body = request.form["body"]
        error = None

        if not search_query:
            error = "Search Query Cant Be Empty"

        if error is not None:
            flash(error)
        else:
            print("the search query is ", search_query)
            posts = get_similar_code(search_query)
            print("the posts are ", posts)
            return render_template("search/index.html")

    return render_template("search/create.html")

@bp.route("/posts")
def blog_posts():
    """Show all the posts, most recent first."""
    db = get_db()
    posts = db.execute(
        "SELECT p.id, title, body, created, author_id, username"
        " FROM post p JOIN user u ON p.author_id = u.id"
        " ORDER BY created DESC"
    ).fetchall()
    return render_template("blog/index.html", posts=posts)


def get_post(id, check_author=True):
    """Get a post and its author by id.

    Checks that the id exists and optionally that the current user is
    the author.

    :param id: id of post to get
    :param check_author: require the current user to be the author
    :return: the post with author information
    :raise 404: if a post with the given id doesn't exist
    :raise 403: if the current user isn't the author
    """
    post = (
        get_db()
        .execute(
            "SELECT p.id, title, body, created, author_id, username"
            " FROM post p JOIN user u ON p.author_id = u.id"
            " WHERE p.id = ?",
            (id,),
        )
        .fetchone()
    )

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post["author_id"] != g.user["id"]:
        abort(403)

    return post


@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    """Create a new post for the current user."""
    print("in blog create ")
    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "INSERT INTO post (title, body, author_id) VALUES (?, ?, ?)",
                (title, body, g.user["id"]),
            )
            db.commit()
            return redirect(url_for("blog.index"))

    return render_template("blog/create.html")


@bp.route("/<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    """Update a post if the current user is the author."""
    post = get_post(id)

    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "UPDATE post SET title = ?, body = ? WHERE id = ?", (title, body, id)
            )
            db.commit()
            return redirect(url_for("blog.index"))

    return render_template("blog/update.html", post=post)


@bp.route("/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    """Delete a post.

    Ensures that the post exists and that the logged in user is the
    author of the post.
    """
    get_post(id)
    db = get_db()
    db.execute("DELETE FROM post WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for("blog.index"))
