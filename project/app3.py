from flask import Flask, render_template, request, redirect, session
from tinydb import TinyDB, Query

app = Flask(
    __name__,
    template_folder="templates3",
    static_folder="static3"
)

app.secret_key = "skrivnost123"

db = TinyDB("db.json")
users = db.table("users")
pets = db.table("pets")

User = Query()

# HOME
@app.route("/")
def home():
    if "user" in session:
        return redirect("/dashboard")
    return redirect("/login")

# REGISTER
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if users.search(User.username == username):
            return "Uporabnik že obstaja"

        users.insert({
            "username": username,
            "password": password
        })

        return redirect("/login")

    return render_template("register3.html")

# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = users.get(User.username == username)

        if user and user["password"] == password:
            session["user"] = username
            return redirect("/dashboard")

        return "Napačen login"

    return render_template("login3.html")

# DASHBOARD
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")

    all_pets = pets.all()
    return render_template("dashboard3.html", pets=all_pets)

# ADD PET
@app.route("/add", methods=["GET", "POST"])
def add():
    if "user" not in session:
        return redirect("/login")

    if request.method == "POST":
        name = request.form["name"]
        animal = request.form["animal"]
        description = request.form["description"]
        location = request.form["location"]
        contact = request.form["contact"]
        status = request.form["status"]

        pets.insert({
            "name": name,
            "animal": animal,
            "description": description,
            "location": location,
            "contact": contact,
            "status": status,
            "owner": session["user"]
        })

        return redirect("/dashboard")

    return render_template("add_pet3.html")

# DETAIL
@app.route("/pet/<int:pet_id>")
def pet_detail(pet_id):
    pet = pets.get(doc_id=pet_id)
    if not pet:
        return "Pet ne obstaja"

    return render_template("detail3.html", pet=pet)

# RUN
if __name__ == "__main__":
    app.run(debug=True)