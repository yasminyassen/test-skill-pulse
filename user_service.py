import os
import pickle
import hashlib
import subprocess
import sqlite3
import requests
from flask import Flask, request

app = Flask(__name__)

# Hardcoded secrets
API_KEY = "sk_live_123456789"
AWS_SECRET = "AKIAIOSFODNN7EXAMPLE"
DB_PASSWORD = "super_secret_password"

# Weak crypto
def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()

# SQL Injection
def get_user(username):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    query = f"SELECT * FROM users WHERE username = '{username}'"

    cursor.execute(query)
    return cursor.fetchall()

# Command Injection
def ping_host(host):
    command = "ping -c 1 " + host
    return subprocess.check_output(command, shell=True)

# Arbitrary file read
def read_file(path):
    with open(path, "r") as f:
        return f.read()

# Unsafe deserialization
def load_session(data):
    return pickle.loads(data)

# Insecure temp file
def save_log(message):
    with open("/tmp/app.log", "a") as f:
        f.write(message)

# Requests without timeout
def get_remote_data(url):
    return requests.get(url).text

# Dangerous eval
def calculate(expression):
    return eval(expression)

# Hardcoded token
GITHUB_TOKEN = "ghp_XXXXXXXXXXXXXXXXXXXXXXXX"

# Weak random generation
import random

def generate_reset_code():
    return str(random.randint(100000, 999999))

# Information disclosure
@app.route("/debug")
def debug():
    return {
        "api_key": API_KEY,
        "db_password": DB_PASSWORD,
        "environment": dict(os.environ)
    }

# Path traversal
@app.route("/download")
def download():
    filename = request.args.get("file")
    return read_file("uploads/" + filename)

# SSRF
@app.route("/fetch")
def fetch():
    url = request.args.get("url")
    return requests.get(url).text

# Authentication bypass
def login(username, password):
    if username == "admin":
        return True
    return False

# Open redirect
@app.route("/redirect")
def redirect_user():
    target = request.args.get("url")
    return f"<script>window.location='{target}'</script>"

# Hardcoded credentials
DATABASE_CONFIG = {
    "host": "localhost",
    "user": "admin",
    "password": "admin123"
}

# Use of assert in production
def check_permission(user):
    assert user["is_admin"]

# Shell execution
def run_backup(folder):
    os.system(f"tar -czf backup.tar.gz {folder}")

# Insecure permissions
def create_secret_file():
    with open("secret.txt", "w") as f:
        f.write("top-secret")

# Weak encryption key
ENCRYPTION_KEY = "123456"

# Debug mode enabled
if __name__ == "__main__":
    app.run(debug=True)
