from app import create_app
from app.extensions import db
from app.models import Puzzle

app=create_app()
with app.app_context():
    puzzle=Puzzle(
        mission_id=1,
        question="""
        I have keys but no locks.
        I have space but no room.
        What am I?
        """,
        answer="keyboard",
        hint="You use it every day on your computer",
        reward_xp=100
    )
    db.session.add(puzzle)
    db.session.commit()

print("Puzzle Added")