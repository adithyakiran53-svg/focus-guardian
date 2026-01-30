from flask import request
from datetime import date
from flask import Flask, render_template, request, redirect, session
import sqlite3
app = Flask(__name__)
app.secret_key = "focus_guardian_secret"


@app.route("/")
def home():
    return "focus guardian is online"


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db", timeout=10)
        c = conn.cursor()

        c.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                  (username, password))

        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db", timeout=10)
        c = conn.cursor()

        c.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )

        user = c.fetchone()
        conn.close()

        if user:
            session["user_id"] = user[0]
            return redirect("/dashboard")
        else:
            return "Invalid username or password"

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")
    today = date.today().isoformat()
    saved = request.args.get("saved")

    conn = sqlite3.connect("database.db", timeout=10)
    c = conn.cursor()

    c.execute(
        "SELECT screen_time, night_usage FROM usage WHERE user_id=? AND date=?", (
            session["user_id"], today)
    )

    usage = c.fetchone()

    conn.close()

    return render_template("dashboard.html", usage=usage, saved=saved)


@app.route("/add_usage", methods=["POST"])
def add_usage():

    if "user_id" not in session:
        return redirect("/login")

    screen_time = int(request.form["screen_time"])
    night_usage = int(request.form["night_usage"])
    today = date.today().isoformat()

    conn = sqlite3.connect("database.db", timeout=10)
    c = conn.cursor()

    c.execute(
        "SELECT id FROM usage WHERE user_id=? AND date=?", (
            session["user_id"], today)
    )

    existing = c.fetchone()

    if existing:
        c.execute(
            "UPDATE usage SET screen_time=?, night_usage=? WHERE id=?", (
                screen_time, night_usage, existing[0])

        )
    else:
        c.execute(
            "INSERT INTO usage (user_id, date, screen_time, night_usage) VALUES (?, ?, ?, ?)", (
                session["user_id"], today, screen_time, night_usage)
        )

    conn.commit()
    conn.close()

    return redirect("/dashboard?saved=1")


if __name__ == "__main__":
    app.run()
