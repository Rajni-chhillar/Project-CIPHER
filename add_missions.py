from app import create_app
from app.extensions import db
from app.models import Mission

app=create_app()
with app.app_context():

    mission=Mission(
        title="The Missing Scientist",
        description="""
        A famous scientist disappeared
        after creating an AI invention.
        Find the hidden clues.
        """,
        difficulty="Medium",
        reward_xp=200,
        is_locked=False
    )
    db.session.add(mission)
    db.session.commit()

print("Mission Added")