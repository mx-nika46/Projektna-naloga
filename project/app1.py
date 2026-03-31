from flask import Flask, render_template, request, session
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/notes.db'
db = SQLAlchemy(app)


# homepage
@app.route("/")
def home():
    if "user" in session:
        return redirect("/dashboard")
    return redirect("/login")

