from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required,
    get_jwt
)
from config import Config
from models import Stream, db, User, Course, Semester
from flask.cli import with_appcontext
import click

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
jwt = JWTManager(app)

# ---------------- Database init CLI ----------------

@app.cli.command("init-db")
@with_appcontext
def init_db():
    """Initialize the database (create tables)."""
    db.create_all()
    click.echo("✅ Database initialized")

# ---------------- Auth & pages ----------------

@app.route("/")
def home():
    return redirect(url_for("login_page"))

# ... [rest of your routes stay unchanged] ...

# ---------------- Main ----------------

if __name__ == "__main__":
    # Running via `python app.py` will start the server—but won't auto-create tables.
    app.run(host="0.0.0.0", port=5000, debug=True)
