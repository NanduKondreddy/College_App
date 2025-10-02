# seed.py

from models import db, User, Stream, Course, Semester

def seed_users():
    """Create admin & faculty if none exist."""
    if User.query.count() == 0:
        admin = User(username="admin", role="admin")
        admin.set_password("admin123")
        faculty = User(username="faculty", role="faculty")
        faculty.set_password("faculty123")
        db.session.add_all([admin, faculty])

def seed_demo_data():
    """Populate streams, courses, and semesters once."""
    if Stream.query.count() > 0:
        return

    # Streams
    btech = Stream(name="BTech")
    mtech = Stream(name="MTech")
    mba   = Stream(name="MBA")
    db.session.add_all([btech, mtech, mba])
    db.session.flush()

    # Courses
    courses = [
        Course(name="CSE",        stream_id=btech.id),
        Course(name="ECE",        stream_id=btech.id),
        Course(name="Mechanical", stream_id=btech.id),
        Course(name="Civil",      stream_id=btech.id),
        Course(name="AI & DS",    stream_id=mtech.id),
        Course(name="VLSI",       stream_id=mtech.id),
        Course(name="Finance",    stream_id=mba.id),
        Course(name="Marketing",  stream_id=mba.id),
        Course(name="HR",         stream_id=mba.id),
    ]
    db.session.add_all(courses)
    db.session.flush()

    # Semesters specs: (course, count, seats)
    sem_specs = [
        (courses[0], 8, 60), (courses[1], 8, 60),
        (courses[2], 8, 60), (courses[3], 8, 60),
        (courses[4], 4, 30), (courses[5], 4, 30),
        (courses[6], 4, 40), (courses[7], 4, 40),
        (courses[8], 4, 40),
    ]
    for course, count, seats in sem_specs:
        for number in range(1, count + 1):
            db.session.add(
                Semester(
                    number=number,
                    course_id=course.id,
                    available_seats=seats
                )
            )

def run():
    """Seed the database within the Flask app context."""
    from app import app
    with app.app_context():
        # ensure tables exist
        db.create_all()
        # run seeds
        seed_users()
        seed_demo_data()
        db.session.commit()
        print("✅ Database seeded successfully")

if __name__ == "__main__":
    run()
