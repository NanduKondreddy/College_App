from app import app, db
from models import User, Stream, Course, Semester

def seed_users():
    if User.query.count() == 0:
        admin = User(username="admin", role="admin")
        admin.set_password("admin123")
        faculty = User(username="faculty", role="faculty")
        faculty.set_password("faculty123")
        db.session.add_all([admin, faculty])

def seed_demo_data():
    if Stream.query.count() > 0:
        return

    btech = Stream(name="BTech")
    mtech = Stream(name="MTech")
    mba   = Stream(name="MBA")
    db.session.add_all([btech, mtech, mba])
    db.session.flush()

    # BTech Courses
    cse   = Course(name="CSE", stream_id=btech.id)
    ece   = Course(name="ECE", stream_id=btech.id)
    mech  = Course(name="Mechanical", stream_id=btech.id)
    civil = Course(name="Civil", stream_id=btech.id)

    # MTech Courses
    ai_ds = Course(name="AI & DS", stream_id=mtech.id)
    vlsi  = Course(name="VLSI", stream_id=mtech.id)

    # MBA Courses
    finance   = Course(name="Finance", stream_id=mba.id)
    marketing = Course(name="Marketing", stream_id=mba.id)
    hr        = Course(name="HR", stream_id=mba.id)

    db.session.add_all([cse, ece, mech, civil, ai_ds, vlsi, finance, marketing, hr])
    db.session.flush()

    # Add semesters
    for course in [cse, ece, mech, civil]:
        for i in range(1, 9):  # 8 semesters for BTech
            db.session.add(Semester(number=i, course_id=course.id, available_seats=60))

    for course in [ai_ds, vlsi]:
        for i in range(1, 5):  # 4 semesters for MTech
            db.session.add(Semester(number=i, course_id=course.id, available_seats=30))

    for course in [finance, marketing, hr]:
        for i in range(1, 5):  # 4 semesters for MBA
            db.session.add(Semester(number=i, course_id=course.id, available_seats=40))

if __name__ == "__main__":
    with app.app_context():
        db.drop_all()
        db.create_all()
        seed_users()
        seed_demo_data()
        db.session.commit()
        print("✅ Database seeded successfully")
