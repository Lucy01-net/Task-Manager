from flask import Flask, render_template, request, redirect, session
import json
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "your_secret_key_here"  # use any random string

# ---------------- USERS ---------------- #

def load_users():
    if os.path.exists("users.json"):
        with open("users.json", "r") as f:
            return json.load(f)
    return {}

def save_users():
    with open("users.json", "w") as f:
        json.dump(users, f, indent=4)

users = load_users()

# ---------------- TASK HELPERS ---------------- #

def get_user_tasks():
    username = session.get("username")
    if username and username in users:
        return users[username]["tasks"]
    return []

# ---------------- ROUTES: TASKS ---------------- #

@app.route("/")
def index():
    if "username" not in session:
        return redirect("/login")

    tasks = get_user_tasks()
    return render_template("index.html", tasks=tasks)

@app.route("/add", methods=["POST"])
def add():
    if "username" not in session:
        return redirect("/login")

    tasks = get_user_tasks()
    task_text = request.form.get("task")

    if task_text:
        tasks.append({"text": task_text, "completed": False})
        save_users()

    return redirect("/")

@app.route("/delete/<int:task_id>")
def delete(task_id):
    if "username" not in session:
        return redirect("/login")

    tasks = get_user_tasks()

    if 0 <= task_id < len(tasks):
        tasks.pop(task_id)
        save_users()

    return redirect("/")

@app.route("/edit/<int:task_id>")
def edit(task_id):
    if "username" not in session:
        return redirect("/login")

    tasks = get_user_tasks()

    if 0 <= task_id < len(tasks):
        return render_template("edit.html", task=tasks[task_id]["text"], task_id=task_id)

    return redirect("/")

@app.route("/update/<int:task_id>", methods=["POST"])
def update(task_id):
    if "username" not in session:
        return redirect("/login")

    tasks = get_user_tasks()
    new_text = request.form.get("task")

    if new_text and 0 <= task_id < len(tasks):
        tasks[task_id]["text"] = new_text
        save_users()

    return redirect("/")

@app.route("/complete/<int:task_id>")
def complete(task_id):
    if "username" not in session:
        return redirect("/login")

    tasks = get_user_tasks()

    if 0 <= task_id < len(tasks):
        tasks[task_id]["completed"] = not tasks[task_id]["completed"]
        save_users()

    return redirect("/")

@app.route("/view/<int:task_id>")
def view(task_id):
    if "username" not in session:
        return redirect("/login")

    tasks = get_user_tasks()

    if 0 <= task_id < len(tasks):
        return render_template("view.html", task=tasks[task_id], task_id=task_id)

    return redirect("/")

# ---------------- AUTH ---------------- #

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            return "Username and password are required"

        if username in users:
            return "User already exists"

        users[username] = {
            "password": generate_password_hash(password),
            "tasks": []
        }
        save_users()
        return redirect("/login")

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username in users and check_password_hash(users[username]["password"], password):
            session["username"] = username
            return redirect("/")
        else:
            return "Invalid username or password"

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect("/login")

# ---------------- RUN ---------------- #

if __name__ == "__main__":
    app.run(debug=True)
