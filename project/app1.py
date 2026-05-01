from flask import Flask, render_template, request, redirect, session, jsonify
from tinydb import TinyDB, Query

app = Flask(__name__)
app.secret_key = "skrivnost"

# -------------------------
# PODATKOVNA BAZA
# -------------------------
db = TinyDB("db.json")
users = db.table("users")

User = Query()

# -------------------------
# HOME
# -------------------------
@app.route("/")
def home():
    if "user" in session:
        return redirect("/dashboard")
    return redirect("/login")


# -------------------------
# REGISTER
# -------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # preveri če obstaja
        if users.search(User.username == username):
            return "Uporabnik že obstaja"

        # shrani v bazo
        users.insert({
            "username": username,
            "password": password
        })

        return redirect("/login")

    return render_template("register.html")


# -------------------------
# LOGIN + SESSION
# -------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = users.get(User.username == username)

        if user and user["password"] == password:
            session["user"] = username   # SESSION
            return redirect("/dashboard")

        return "Napačen login"

    return render_template("login.html")


# -------------------------
# DASHBOARD (SINHRONO)
# -------------------------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")

    return render_template("dashboard.html", user=session["user"])


# -------------------------
# AJAX (ASINHRONO)
# -------------------------
@app.route("/api/user")
def api_user():
    if "user" not in session:
        return jsonify({"error": "Nisi prijavljen"})

    user = users.get(User.username == session["user"])
    return jsonify(user)


# -------------------------
# LOGOUT
# -------------------------
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")


# -------------------------
# RUN
# -------------------------
if __name__ == "__main__":
    app.run(debug=True)