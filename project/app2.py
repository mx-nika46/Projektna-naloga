from flask import Flask, render_template, request, redirect, session, jsonify
from tinydb import TinyDB, Query

app = Flask(
    __name__,
    template_folder="templates2",
    static_folder="static2"
)

app.secret_key = "skrivnost123"

# -------------------------
# BAZA
# -------------------------
db = TinyDB("db.json")
users = db.table("users")
posts = db.table("posts")

User = Query()

# -------------------------
# HOME
# -------------------------
@app.route("/")
def index():
    return redirect("/login2")

# -------------------------
# REGISTER
# -------------------------
@app.route("/register2", methods=["GET", "POST"])
def register2():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if users.search(User.username == username):
            return "Uporabnik že obstaja"

        users.insert({
            "username": username,
            "password": password
        })

        return redirect("/login2")

    return render_template("register2.html")

# -------------------------
# LOGIN (SESSION)
# -------------------------
@app.route("/login2", methods=["GET", "POST"])
def login2():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = users.get((User.username == username) & (User.password == password))

        if user:
            session["user"] = username
            return redirect("/objave")

        return "Napačni podatki"

    return render_template("login2.html")

# -------------------------
# OBJAVE (SINHRONO)
# -------------------------
@app.route("/objave")
def objave():
    if "user" not in session:
        return redirect("/login2")

    vsi_posts = posts.all()
    vsi_posts.reverse()

    return render_template("objave.html", posts=vsi_posts)

# -------------------------
# DODAJ OBJAVO (TEXT + URL SLIKE)
# -------------------------
@app.route("/add2", methods=["POST"])
def add2():
    if "user" not in session:
        return redirect("/login2")

    text = request.form["text"]
    image_url = request.form.get("image_url", "")

    posts.insert({
        "user": session["user"],
        "text": text,
        "image": image_url
    })

    return redirect("/objave")

# -------------------------
# AJAX
# -------------------------
@app.route("/api/posts2")
def api_posts2():
    return jsonify(posts.all())

# -------------------------
# RUN
# -------------------------
if __name__ == "__main__":
    app.run(debug=True)