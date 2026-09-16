from app import create_app
from app.models import Mission

app = create_app()
with app.app_context():

    missions = Mission.query.all()
    print("Total Missions:", len(missions))
    for m in missions:
        print(
            m.id,
            m.title,
            m.difficulty,
            m.reward_xp
        )