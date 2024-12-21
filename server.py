import os
import random
import sqlite3
from datetime import datetime

from dotenv import load_dotenv
from flask import Flask, g, redirect, render_template, request, url_for
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import check_password_hash, generate_password_hash

import sqlite_utils
from opengraph_utils import get_title_description_image

load_dotenv()


app = Flask(__name__)
auth = HTTPBasicAuth()


DATABASE_PATH = os.environ.get("DATABASE_PATH")
SUBMIT_PASSWORD = os.environ.get("SUBMIT_PASSWORD")
COLORS = [
    # full tailwind color names so that they're picked up by tailwind
    "bg-amber-50",
    "bg-blue-50",
    "bg-cyan-50",
    "bg-emerald-50",
    "bg-fuchsia-50",
    "bg-gray-50",
    "bg-green-50",
    "bg-indigo-50",
    "bg-lime-50",
    "bg-neutral-50",
    "bg-orange-50",
    "bg-pink-50",
    "bg-purple-50",
    "bg-red-50",
    "bg-rose-50",
    "bg-sky-50",
    "bg-slate-50",
    "bg-stone-50",
    "bg-teal-50",
    "bg-violet-50",
    "bg-yellow-50",
    "bg-zinc-50",
]

ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")

users = {ADMIN_USERNAME: generate_password_hash(ADMIN_PASSWORD)}


@auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users.get(username), password):
        return username


def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE_PATH)
        db.row_factory = sqlite3.Row
        # create table with the following cols:
        # timestamp, url, og_title, og_description, og_image_url
        db.execute(
            "CREATE TABLE IF NOT EXISTS reccs (timestamp DATETIME, url TEXT, og_title TEXT, og_description TEXT, og_image_url TEXT)"
        )

    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


def get_all_recs_for_index():
    cur = get_db().execute("select rowid,* from reccs order by timestamp desc")
    all_reccs = cur.fetchall()
    cur.close()
    reccs_out = []
    for recc in all_reccs:
        recc_dict = dict(recc)
        recc_dict["bg_color"] = random.choice(COLORS)
        # convert timestamp int (seconds) into dd/mm/yyyy
        recc_dict["timestamp"] = datetime.fromtimestamp(
            recc_dict["timestamp"]
        ).strftime("%d/%m/%Y")
        reccs_out.append(recc_dict)
    return reccs_out


@app.route("/")
def index():
    reccs_out = get_all_recs_for_index()
    return render_template("index.html", all_reccs=reccs_out)


@app.route("/submit/", methods=["GET", "POST"])
def submit():
    if request.method == "POST":
        password = request.form["password"]
        if password != SUBMIT_PASSWORD:
            return "no"
        url = request.form["url"]
        timestamp = datetime.now()

        opengraph_data = {}
        try:
            opengraph_data = get_title_description_image(url)
        except:
            pass
        title = opengraph_data.get("title", "")
        description = opengraph_data.get("description", "")
        image = opengraph_data.get("image", "")

        db = get_db()
        db.execute(
            """INSERT INTO reccs
                (timestamp, url, og_title, og_description, og_image_url)
                VALUES (?, ?, ?, ?, ?)
            """,
            (timestamp, url, title, description, image),
        )
        db.commit()
        return redirect(url_for("index"))
    return render_template("submit.html")


@app.route("/admin/")
@auth.login_required
def admin():
    reccs_out = get_all_recs_for_index()
    return render_template("index.html", all_reccs=reccs_out, is_admin=True)


@app.route("/delete")
@auth.login_required
def delete():
    recc_id = request.args.get("recc_id")
    db = get_db()
    db.execute("DELETE FROM reccs WHERE rowid = ?", (recc_id,))
    db.commit()
    return redirect(url_for("admin"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
