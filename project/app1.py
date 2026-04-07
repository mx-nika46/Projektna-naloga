from flask import Flask, render_template, request, redirect, session, jsonify
from tinydb import TinyDB, Query

app = Flask( __name__, template_folder="templates1", static_folder="static1")
app.secret_key = "skrivnost123"

db = TinyDB("db.json")
users = db.table("users")

User = Query()

# homepage
@app.route("/")
def home():
    if "user" in session:
        return redirect("/dashboard")
    return redirect("/login")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if users.search(User.username == username):
            return "Uporabnik že obstaja"
        
        users.insert({"username" : username, "password" : password, "note" : ""})
        return redirect("/login")

        # print(username, password)
    return render_template("register.html")

@app.route("/login", methods = ["GET", "POST"])
def login():

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = users.get(User.username == username)
        #print(user)

        if user and user["password"] == password:
            session["user"] = username 
            return redirect("/dashboard")
        
        return "Napačen login"

    return render_template("login.html")

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user" not in session:
        return redirect("/login")
    user = users.get(User.username == session["user"])

    if "notes" not in user:
        user["notes"] = [{"title": "", "content": ""} for _ in range(3)]
        users.update({"notes": user["notes"]}, User.username == session["user"])

    if request.method == "POST":
        action = request.form.get("action")
        index = int(request.form.get("note_index", 0))

      
        while len(user["notes"]) <= index:
            user["notes"].append({"title": "", "content": ""})

        if action == "save":
            user["notes"][index]["title"] = request.form.get("title", "")
            user["notes"][index]["content"] = request.form.get("content", "")
        elif action == "delete":
            user["notes"][index] = {"title": "", "content": ""}

       
        users.update({"notes": user["notes"]}, User.username == session["user"])

    user = users.get(User.username == session["user"])
    return render_template("dashboard.html", user=session["user"], notes=user["notes"])

app.run(debug=1)