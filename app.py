# app.py

import os
import click

from flask import (
    Flask, render_template, request, jsonify,
    redirect, session, flash
)
from flask.cli import with_appcontext
from flask_jwt_extended import (
    JWTManager, create_access_token,
    jwt_required, get_jwt
)

from config import Config
from models import db, User, Stream, Course, Semester
import seed  # our standalone seed.py

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
jwt = JWTManager(app)


# ---------------- Auto‐Seed on First Request ----------------

_seeded = False

@app.before_request
def _auto_seed_once():
    global _seeded
    if _seeded:
        return

    app.logger.info(f"🔍 Using DB URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
    db.create_all()

    # Only seed if no users exist
    if User.query.count() == 0:
        seed.seed_users()
        seed.seed_demo_data()
        db.session.commit()
        app.logger.info("✅ Auto‐seeded database on startup")

    _seeded = True


# ---------------- CLI Commands ----------------

@app.cli.command("init-db")
@with_appcontext
def init_db():
    """Create all tables."""
    db.create_all()
    click.echo("✅ Database initialized")


@app.cli.command("seed-db")
@with_appcontext
def cli_seed_db():
    """Insert default users and demo data."""
    seed.seed_users()
    seed.seed_demo_data()
    db.session.commit()
    click.echo("✅ seed-db complete")


@app.cli.command("full-refresh")
@with_appcontext
def cli_full_refresh():
    """Drop all tables, recreate schema, then seed everything."""
    db.drop_all()
    db.create_all()
    seed.seed_users()
    seed.seed_demo_data()
    db.session.commit()
    click.echo("✅ full-refresh complete")

@app.route('/seed-all')
def seed_all():
    db.create_all()
    if User.query.count() == 0:
        from seed import seed_users, seed_demo_data
        seed_users()
        seed_demo_data()
        db.session.commit()
        return '✅ Database seeded', 200
    return '⚠️ Already seeded', 200


# ---------------- Routes ----------------

@app.route("/")
def home():
    return redirect("/login")

@app.route("/ping")
def ping():
    return "App is alive!"

@app.route("/login", methods=["GET", "POST"])
def login_page():
    if request.method == "POST":
        username      = request.form.get("username", "").strip()
        password      = request.form.get("password", "").strip()
        selected_role = request.form.get("role", "").strip()

        user = User.query.filter_by(
            username=username, role=selected_role
        ).first()

        if not user or not user.check_password(password):
            return render_template("login.html",
                                   error="Invalid credentials or role")

        token = create_access_token(
            identity=str(user.id),
            additional_claims={"role": user.role}
        )
        session["jwt"]      = token
        session["role"]     = user.role
        session["username"] = user.username

        dest = "faculty" if user.role == "faculty" else "admin"
        return redirect(f"/{dest}")

    return render_template("login.html")


@app.route("/admin")
def admin_page():
    token = session.get("jwt", "")
    role  = session.get("role")
    if not token or role != "admin":
        flash("Unauthorized: Admin access required.")
        return redirect("/login")
    return render_template("admin.html", jwt=token)


@app.route("/faculty")
def faculty_page():
    token = session.get("jwt", "")
    role  = session.get("role")
    if not token or role != "faculty":
        flash("Unauthorized: Faculty access required.")
        return redirect("/login")
    return render_template("faculty.html")


# ---------------- API Endpoints ----------------

@app.route("/api/streams")
def get_streams():
    return jsonify([{"id": s.id, "name": s.name}
                    for s in Stream.query.all()])


@app.route("/api/courses/<int:stream_id>")
def get_courses(stream_id):
    return jsonify([{"id": c.id, "name": c.name}
                    for c in Course.query.filter_by(stream_id=stream_id)])


@app.route("/api/semesters/<int:course_id>")
def get_semesters(course_id):
    return jsonify([
        {"id": s.id, "number": s.number, "available_seats": s.available_seats}
        for s in Semester.query.filter_by(course_id=course_id)
    ])


@app.route("/api/update_seats", methods=["POST"])
@jwt_required()
def update_seats():
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json(silent=True) or {}
    try:
        semester_id = int(data["semester_id"])
        new_count   = int(data["count"])
    except (KeyError, ValueError):
        return jsonify({"error": "Invalid input"}), 400

    sem = Semester.query.get(semester_id)
    if not sem:
        return jsonify({"error": "Semester not found"}), 404

    sem.available_seats = new_count
    db.session.commit()
    return jsonify({
        "message": "Updated successfully",
        "semester_id": semester_id,
        "available": new_count
    })


# ---------------- Auth Utilities ----------------

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()
        role     = request.form["role"].strip()

        if role not in ("faculty", "admin"):
            return render_template("register.html",
                                   error="Role must be faculty or admin")

        if User.query.filter_by(username=username).first():
            return render_template("register.html",
                                   error="Username already exists")

        user = User(username=username, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash("Registration successful! Please login.")
        return redirect("/login")

    return render_template("register.html")


@app.route("/forgot", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        username     = request.form["username"].strip()
        new_password = request.form["new_password"].strip()

        user = User.query.filter_by(username=username).first()
        if not user:
            return render_template("forgot.html",
                                   error="User not found")

        user.set_password(new_password)
        db.session.commit()

        flash("Password reset successful! Please login with your new password.")
        return redirect("/login")

    return render_template("forgot.html")


@app.route("/logout")
def logout():
    session.pop("jwt", None)
    flash("Logged out successfully.")
    return redirect("/login")


# ---------------- Main ----------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
