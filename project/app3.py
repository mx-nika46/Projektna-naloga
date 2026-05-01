from flask import Flask, render_template, request, redirect, session, jsonify
from tinydb import TinyDB, Query

app = Flask(__name__)
app.secret_key = "skrivnost"

# -------------------------
# PODATKOVNA BAZA
# -------------------------
db = TinyDB("db.json")
users = db.table("users")
pets = db.table("pets")

User = Query()

# -------------------------
# LOGIN (SESSION)
# -------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = users.get(User.username == username)

        if user and user["password"] == password:
            session["user"] = username   # shrani v session
            return redirect("/home")

        return "Napačen login"

    return render_template("login.html")


# -------------------------
# HOME (SINHRONI KLIC)
# -------------------------
@app.route("/home")
def home():
    if "user" not in session:
        return redirect("/login")

    all_pets = pets.all()
    return render_template("home.html", pets=all_pets)


# -------------------------
# DODAJ (SINHRONO)
# -------------------------
@app.route("/add", methods=["POST"])
def add():
    if "user" not in session:
        return redirect("/login")

    name = request.form["name"]

    pets.insert({
        "name": name,
        "owner": session["user"]
    })

    return redirect("/home")


# -------------------------
# AJAX (ASINHRONI KLIC)
# -------------------------
@app.route("/api/pets")
def api_pets():
    all_pets = pets.all()
    return jsonify(all_pets)


# -------------------------
# LOGOUT
# -------------------------
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")


# -------------------------
# ZAGON
# -------------------------
if __name__ == "__main__":
    app.run(debug=True)