from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required,
    get_jwt
)
from config import Config
from models import Stream, db, User, Course, Semester

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
jwt = JWTManager(app)

@app.route("/")
def home():
    return redirect(url_for("login_page"))

# ---------------- Auth & pages ----------------

@app.route("/login", methods=["GET", "POST"])
def login_page():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        selected_role = request.form.get("role", "").strip()

        # ✅ Enforce role match at login
        user = User.query.filter_by(username=username, role=selected_role).first()
        if not user or not user.check_password(password):
            return render_template("login.html", error="Invalid credentials or role")

        token = create_access_token(
            identity=str(user.id),
            additional_claims={"role": user.role, "username": user.username}
        )
        session["jwt"] = token
        session["role"] = user.role
        session["username"] = user.username

        return redirect(url_for("faculty_page" if user.role == "faculty" else "admin_page"))

    return render_template("login.html")

# ✅ Guarded routes
@app.route("/admin")
def admin_page():
    token = session.get("jwt", "")
    role = session.get("role")
    if not token or role != "admin":
        flash("Unauthorized: Admin access required.")
        return redirect(url_for("login_page"))
    return render_template("admin.html", jwt=token)

@app.route("/faculty")
def faculty_page():
    token = session.get("jwt", "")
    role = session.get("role")
    if not token or role != "faculty":
        flash("Unauthorized: Faculty access required.")
        return redirect(url_for("login_page"))
    return render_template("faculty.html")

# ---------------- API endpoints ----------------
# Get all streams
@app.route("/api/streams", methods=["GET"])
def get_streams():
    items = Stream.query.all()
    return jsonify([{"id": s.id, "name": s.name} for s in items])


# Get courses under a stream
@app.route("/api/courses/<int:stream_id>", methods=["GET"])
def get_courses(stream_id):
    items = Course.query.filter_by(stream_id=stream_id).all()
    return jsonify([{"id": c.id, "name": c.name} for c in items])


# Get semesters under a course (✅ no branches anymore)
# should use course_id, not branch_id
@app.route("/api/semesters/<int:course_id>", methods=["GET"])
def get_semesters(course_id):
    items = Semester.query.filter_by(course_id=course_id).all()
    return jsonify([
      {"id": s.id, "number": s.number, "available_seats": s.available_seats}
      for s in items
    ])



# Get seat availability for a semester
@app.route("/api/seats/<int:semester_id>", methods=["GET"])
def get_seats(semester_id):
    s = Semester.query.get(semester_id)
    if not s:
        return jsonify({"error": "Not found"}), 404
    return jsonify({"semester_id": s.id, "available": s.available_seats})


# Update seat availability (Admin only)
@app.route("/api/update_seats", methods=["POST"])
@jwt_required()
def update_seats():
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Missing JSON body"}), 400

    try:
        semester_id = int(data.get("semester_id"))
        new_count = int(data.get("count"))
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid semester_id or count"}), 400

    s = Semester.query.get(semester_id)
    if not s:
        return jsonify({"error": "Semester not found"}), 404

    s.available_seats = new_count
    db.session.commit()
    return jsonify({
        "message": "Updated successfully",
        "semester_id": semester_id,
        "available": new_count
    })

# ---------------- Register & Forgot ----------------

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()
        role = request.form["role"].strip()

        if role not in ("faculty", "admin"):
            return render_template("register.html", error="Role must be faculty or admin")

        if User.query.filter_by(username=username).first():
            return render_template("register.html", error="Username already exists")

        user = User(username=username, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash("Registration successful! Please login.")
        return redirect(url_for("login_page"))

    return render_template("register.html")

@app.route("/forgot", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        username = request.form["username"].strip()
        new_password = request.form["new_password"].strip()

        user = User.query.filter_by(username=username).first()
        if not user:
            return render_template("forgot.html", error="User not found")

        user.set_password(new_password)
        db.session.commit()

        flash("Password reset successful! Please login with your new password.")
        return redirect(url_for("login_page"))

    return render_template("forgot.html")

@app.route("/logout")
def logout():
    session.pop("jwt", None)
    flash("Logged out successfully.")
    return redirect(url_for("login_page"))

# ---------------- Main ----------------

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
