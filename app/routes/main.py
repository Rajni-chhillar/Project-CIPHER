from flask import Blueprint, render_template
from app.models import User, Mission, MissionCompletion

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():

    total_agents = User.query.count()
    total_missions = Mission.query.count()
    total_cases = MissionCompletion.query.count()
    total_countries = 0
    missions = Mission.query.order_by(
        Mission.id.asc()
    ).limit(6).all()

    return render_template(
        "index.html",
        total_agents=total_agents,
        total_missions=total_missions,
        total_cases=total_cases,
        total_countries=total_countries,
        missions=missions
    )

@main_bp.route("/about")
def about():
    return render_template("about.html")