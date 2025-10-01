from app import app, db
from models import User, Stream, Course, Semester

def full_refresh():
    db.drop_all()
    db.create_all()

    # seed users
    admin = User(username="admin", role="admin")
    admin.set_password("Nandu@2201")
    faculty = User(username="faculty", role="faculty")
    faculty.set_password("faculty123")
    db.session.add_all([admin, faculty])

    # seed streams
    btech = Stream(name="BTech")
    mtech = Stream(name="MTech")
    mba   = Stream(name="MBA")
    db.session.add_all([btech, mtech, mba])
    db.session.flush()

    # seed courses
    cse   = Course(name="CSE", stream_id=btech.id)
    ece   = Course(name="ECE", stream_id=btech.id)
    mech  = Course(name="Mechanical", stream_id=btech.id)
    civil = Course(name="Civil", stream_id=btech.id)
    ai_ds = Course(name="AI & DS", stream_id=mtech.id)
    vlsi  = Course(name="VLSI", stream_id=mtech.id)
    fin   = Course(name="Finance", stream_id=mba.id)
    mkt   = Course(name="Marketing", stream_id=mba.id)
    hr    = Course(name="HR", stream_id=mba.id)
    db.session.add_all([cse,ece,mech,civil,ai_ds,vlsi,fin,mkt,hr])
    db.session.flush()

    # seed semesters
    for course, sem_count, seats in [
        (cse,8,60),(ece,8,60),(mech,8,60),(civil,8,60),
        (ai_ds,4,30),(vlsi,4,30),
        (fin,4,40),(mkt,4,40),(hr,4,40),
    ]:
        for i in range(1, sem_count+1):
            db.session.add(
                Semester(number=i, course_id=course.id, available_seats=seats)
            )

    db.session.commit()
    print("✅ Full refresh complete.")

if __name__ == "__main__":
    with app.app_context():
        full_refresh()
