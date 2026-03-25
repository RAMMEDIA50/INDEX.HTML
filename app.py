from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import sqlite3
import hashlib

app = Flask(__name__)
CORS(app)

# ---------- DATABASE ----------
def init_db():
    conn = sqlite3.connect("db.sqlite3")
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

def hash_pass(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ---------- ROUTES (PAGES) ----------
@app.route("/")
def login_page():
    return render_template("login.html")

@app.route("/register-page")
def register_page():
    return render_template("register.html")

@app.route("/dashboard")
def dashboard():
    return render_template("index.html")

# ---------- API ----------
@app.route("/register", methods=["POST"])
def register():
    data = request.json

    try:
        conn = sqlite3.connect("db.sqlite3")
        c = conn.cursor()

        c.execute("INSERT INTO users(username,password,role) VALUES(?,?,?)",
                  (data["username"], hash_pass(data["password"]), "member"))

        conn.commit()
        conn.close()

        return jsonify({"status":"success"})
    except:
        return jsonify({"status":"user_exists"})

@app.route("/login", methods=["POST"])
def login():
    data = request.json

    conn = sqlite3.connect("db.sqlite3")
    c = conn.cursor()

    c.execute("SELECT * FROM users WHERE username=? AND password=?",
              (data["username"], hash_pass(data["password"])))

    user = c.fetchone()
    conn.close()

    if user:
        return jsonify({
            "status":"success",
            "role": user[3],
            "username": user[1]
        })
    else:
        return jsonify({"status":"fail"})

# CREATE ADMIN ONCE
@app.route("/create-admin")
def create_admin():
    conn = sqlite3.connect("db.sqlite3")
    c = conn.cursor()

    c.execute("INSERT INTO users(username,password,role) VALUES(?,?,?)",
              ("admin", hash_pass("1234"), "admin"))

    conn.commit()
    conn.close()

    return "Admin created"

# ---------- RUN ----------
if __name__ == "__main__":
    app.run(debug=True)