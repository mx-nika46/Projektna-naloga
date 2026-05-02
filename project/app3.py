from flask import Flask, render_template, request, redirect, session, jsonify
from tinydb import TinyDB, Query

app = Flask(
    __name__,
    template_folder="templates3",
    static_folder="static3"
)

app.secret_key = "skrivnost"

# -------------------------
# BAZA
# -------------------------
db = TinyDB("db.json")
users = db.table("users")
pets = db.table("pets")

User = Query()

# -------------------------
# HOME
# -------------------------
@app.route("/")
def index():
    return redirect("/login3")

# -------------------------
# REGISTER
# -------------------------
@app.route("/register3", methods=["GET", "POST"])
def register3():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if users.search(User.username == username):
            return "Uporabnik že obstaja"

        users.insert({
            "username": username,
            "password": password
        })

        return redirect("/login3")

    return render_template("register3.html")

# -------------------------
# LOGIN
# -------------------------
@app.route("/login3", methods=["GET", "POST"])
def login3():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = users.get(User.username == username)

        if user and user["password"] == password:
            session["user"] = username
            return redirect("/dashboard3")

        return "Napačen login"

    return render_template("login3.html")

# -------------------------
# DASHBOARD
# -------------------------
@app.route("/dashboard3")
def dashboard3():
    if "user" not in session:
        return redirect("/login3")

    all_pets = pets.all()
    return render_template("dashboard3.html", pets=all_pets)

# -------------------------
# ADD PET
# -------------------------
@app.route("/add3", methods=["GET", "POST"])
def add3():
    if "user" not in session:
        return redirect("/login3")

    if request.method == "POST":
        name = request.form["name"]
        type_ = request.form["type"]
        description = request.form["description"]
        status = request.form["status"]
        phone = request.form["phone"]
        image_url = request.form.get("image_url", "")

        pets.insert({
            "name": name,
            "type": type_,
            "description": description,
            "status": status,
            "phone": phone,
            "image": image_url,
            "owner": session["user"],
            "comments": []
        })

        return redirect("/dashboard3")

    return render_template("add_pet3.html")

# -------------------------
# DELETE PET
# -------------------------
@app.route("/delete3/<int:pet_id>")
def delete3(pet_id):
    if "user" not in session:
        return redirect("/login3")

    pet = pets.get(doc_id=pet_id)

    # preveri če je lastnik
    if pet and pet["owner"] == session["user"]:
        pets.remove(doc_ids=[pet_id])

    return redirect("/dashboard3")


# -------------------------
# DETAIL
# -------------------------
@app.route("/pet3/<int:pet_id>")
def detail3(pet_id):
    pet = pets.get(doc_id=pet_id)
    return render_template("detail3.html", pet=pet)

# -------------------------
# KOMENTARJI
# -------------------------
@app.route("/comment3/<int:pet_id>", methods=["POST"])
def comment3(pet_id):
    text = request.form["comment"]

    pet = pets.get(doc_id=pet_id)

    if pet:
        pet["comments"].append(text)
        pets.update({"comments": pet["comments"]}, doc_ids=[pet_id])

    return redirect(f"/pet3/{pet_id}")

# -------------------------
# AJAX
# -------------------------
@app.route("/api/pets3")
def api_pets3():
    return jsonify(pets.all())

# -------------------------
# LOGOUT
# -------------------------
@app.route("/logout3")
def logout3():
    session.pop("user", None)
    return redirect("/login3")

# -------------------------
# RUN
# -------------------------
if __name__ == "__main__":
    app.run(debug=True)