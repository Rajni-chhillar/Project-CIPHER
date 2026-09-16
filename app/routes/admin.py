from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Mission, Puzzle, User, MissionCompletion

admin_bp = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin"
)

@admin_bp.route("/")
@login_required
def dashboard():

    if not current_user.is_admin:
        return "Access Denied", 403

    total_missions=Mission.query.count()
    total_puzzles=Puzzle.query.count()
    total_agents=User.query.filter_by(
        is_admin=False
    ).count()

    completed_missions=MissionCompletion.query.count()
    recent_completions=MissionCompletion.query.order_by(
        MissionCompletion.completed_at.desc()
    ).limit(5).all()
    recent_missions=Mission.query.order_by(
        Mission.created_at.desc()
    ).limit(5).all()

    return render_template(
        "admin/dashboard.html",
        total_missions=total_missions,
        total_puzzles=total_puzzles,
        total_agents=total_agents,
        completed_missions=completed_missions,
        recent_missions=recent_missions,
        recent_completions=recent_completions
    )

@admin_bp.route("/missions")
@login_required
def manage_missions():

    if not current_user.is_admin:
        return "Access Denied", 403

    missions = Mission.query.order_by(
        Mission.id.asc()
    ).all()

    return render_template(
        "admin/missions.html",
        missions=missions
    )

@admin_bp.route("/missions/add", methods=["GET", "POST"])
@login_required
def add_mission():

    if not current_user.is_admin:
        return "Access Denied", 403
    if request.method == "POST":
        title = request.form.get(
            "title",
            ""
        ).strip()
        description = request.form.get(
            "description",
            ""
        ).strip()
        difficulty = request.form.get(
            "difficulty",
            "Medium"
        )
        reward_xp = request.form.get(
            "reward_xp",
            100
        )
        if not title or not description:
            flash(
                "Mission title and description are required.",
                "danger"
            )
            return redirect(
                url_for("admin.add_mission")
            )
        try:
            reward_xp = int(reward_xp)
        except ValueError:
            flash(
                "Reward XP must be a number.",
                "danger"
            )
            return redirect(
                url_for("admin.add_mission")
            )
        mission = Mission(
            title=title,
            description=description,
            difficulty=difficulty,
            reward_xp=reward_xp,
        )
        db.session.add(mission)
        db.session.commit()
        flash(
            "Mission added successfully! 🗺️",
            "success"
        )
        return redirect(
            url_for("admin.manage_missions")
        )
    return render_template(
        "admin/add_mission.html"
    )

@admin_bp.route("/missions/<int:mission_id>/edit", methods=["GET", "POST"])
@login_required
def edit_mission(mission_id):

    if not current_user.is_admin:
        return "Access Denied", 403
    mission = Mission.query.get_or_404(mission_id)
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        difficulty = request.form.get("difficulty", "Medium")
        reward_xp = request.form.get("reward_xp", 100)
        if not title or not description:
            flash(
                "Mission title and description are required.",
                "danger"
            )
            return redirect(
                url_for(
                    "admin.edit_mission",
                    mission_id=mission.id
                )
            )
        try:
            reward_xp = int(reward_xp)
        except ValueError:
            flash(
                "Reward XP must be a number.",
                "danger"
            )
            return redirect(
                url_for(
                    "admin.edit_mission",
                    mission_id=mission.id
                )
            )
        mission.title = title
        mission.description = description
        mission.difficulty = difficulty
        mission.reward_xp = reward_xp

        db.session.commit()
        flash(
            "Mission updated successfully! ✏️",
            "success"
        )
        return redirect(
            url_for("admin.manage_missions")
        )
    return render_template(
        "admin/edit_mission.html",
        mission=mission
    )

@admin_bp.route("/missions/<int:mission_id>/delete",methods=["POST"])
@login_required
def delete_mission(mission_id):

    if not current_user.is_admin:
        return "Access Denied", 403
    mission = Mission.query.get_or_404(mission_id)
    db.session.delete(mission)
    db.session.commit()
    flash(
        "Mission deleted successfully! 🗑️",
        "success"
    )
    return redirect(
        url_for("admin.manage_missions")
    )


@admin_bp.route("/puzzles/add", methods=["GET", "POST"])
@login_required
def add_puzzle():

    if not current_user.is_admin:
        return "Access Denied", 403

    missions = Mission.query.order_by(
        Mission.id.asc()
    ).all()
    if request.method == "POST":
        mission_id = request.form.get("mission_id")
        title = request.form.get("title", "").strip()
        description = request.form.get(
            "description",
            ""
        ).strip()
        clue = request.form.get(
            "clue",
            ""
        ).strip()
        question = request.form.get(
            "question",
            ""
        ).strip()
        answer = request.form.get(
            "answer",
            ""
        ).strip()
        order = request.form.get(
            "order",
            1
        )
        xp = request.form.get(
            "xp",
            100
        )
        max_attempts = request.form.get(
            "max_attempts",
            3
        )
        if not mission_id:
            flash(
                "Please select a mission.",
                "danger"
            )
            return redirect(
                url_for("admin.add_puzzle")
            )
        if not title or not question or not answer:
            flash(
                "Title, question and answer are required.",
                "danger"
            )
            return redirect(
                url_for("admin.add_puzzle")
            )
        try:
            order = int(order)
            xp = int(xp)
            max_attempts = int(max_attempts)
        except ValueError:
            flash(
                "Order, XP and attempts must be numbers.",
                "danger"
            )
            return redirect(
                url_for("admin.add_puzzle")
            )
        puzzle = Puzzle(
            mission_id=int(mission_id),
            title=title,
            description=description,
            clue=clue,
            question=question,
            answer=answer,
            order=order,
            xp=xp,
            max_attempts=max_attempts
        )
        db.session.add(puzzle)
        db.session.commit()

        flash(
            "Puzzle added successfully! 🧩",
            "success"
        )
        return redirect(
            url_for("admin.manage_puzzles")
        )

    return render_template(
        "admin/add_puzzle.html",
        missions=missions
    )

@admin_bp.route("/puzzles")
@login_required
def manage_puzzles():

    if not current_user.is_admin:
        return "Access Denied", 403

    puzzles = Puzzle.query.order_by(
        Puzzle.id.asc()
    ).all()

    return render_template(
        "admin/puzzles.html",
        puzzles=puzzles
    )

@admin_bp.route("/puzzles/<int:puzzle_id>/edit", methods=["GET", "POST"])
@login_required
def edit_puzzle(puzzle_id):

    if not current_user.is_admin:
        return "Access Denied", 403
    puzzle = Puzzle.query.get_or_404(puzzle_id)
    missions = Mission.query.order_by(
        Mission.id.asc()
    ).all()
    if request.method == "POST":
        mission_id = request.form.get("mission_id")
        title = request.form.get("title", "").strip()
        description = request.form.get(
            "description",
            ""
        ).strip()
        clue = request.form.get(
            "clue",
            ""
        ).strip()
        question = request.form.get(
            "question",
            ""
        ).strip()
        answer = request.form.get(
            "answer",
            ""
        ).strip()
        order = request.form.get(
            "order",
            1
        )
        xp = request.form.get(
            "xp",
            100
        )
        max_attempts = request.form.get(
            "max_attempts",
            3
        )
        if not mission_id or not title or not question or not answer:
            flash(
                "Mission, title, question and answer are required.",
                "danger"
            )
            return redirect(
                url_for(
                    "admin.edit_puzzle",
                    puzzle_id=puzzle.id
                )
            )
        try:
            mission_id = int(mission_id)
            order = int(order)
            xp = int(xp)
            max_attempts = int(max_attempts)
        except ValueError:
            flash(
                "Order, XP and attempts must be numbers.",
                "danger"
            )
            return redirect(
                url_for(
                    "admin.edit_puzzle",
                    puzzle_id=puzzle.id
                )
            )
        mission = Mission.query.get(mission_id)
        if not mission:
            flash(
                "Selected mission does not exist.",
                "danger"
            )
            return redirect(
                url_for(
                    "admin.edit_puzzle",
                    puzzle_id=puzzle.id
                )
            )
        puzzle.mission_id = mission_id
        puzzle.title = title
        puzzle.description = description
        puzzle.clue = clue
        puzzle.question = question
        puzzle.answer = answer
        puzzle.order = order
        puzzle.xp = xp
        puzzle.max_attempts = max_attempts
        db.session.commit()
        flash(
            "Puzzle updated successfully! ✏️",
            "success"
        )
        return redirect(
            url_for("admin.manage_puzzles")
        )
    return render_template(
        "admin/edit_puzzle.html",
        puzzle=puzzle,
        missions=missions
    )

@admin_bp.route("/puzzles/<int:puzzle_id>/delete", methods=["POST"])
@login_required
def delete_puzzle(puzzle_id):
    if not current_user.is_admin:
        return "Access Denied", 403
    puzzle = Puzzle.query.get_or_404(puzzle_id)
    db.session.delete(puzzle)
    db.session.commit()
    flash(
        "Puzzle deleted successfully! 🗑️",
        "success"
    )
    return redirect(
        url_for("admin.manage_puzzles")
    )

@admin_bp.route("/agents")
@login_required
def manage_agents():

    if not current_user.is_admin:
        return "Access Denied", 403

    agents = User.query.filter_by(
        is_admin=False
    ).order_by(
        User.created_at.desc()
    ).all()

    return render_template(
        "admin/agents.html",
        agents=agents
    )

@admin_bp.route("/leaderboard")
@login_required
def leaderboard():

    if not current_user.is_admin:
        return "Access Denied", 403

    agents = User.query.filter_by(
        is_admin=False
    ).order_by(
        User.xp.desc()
    ).all()

    return render_template(
        "admin/leaderboard.html",
        agents=agents
    )

@admin_bp.route("/analytics")
@login_required
def analytics():

    if not current_user.is_admin:
        return "Access Denied", 403
    total_agents = User.query.filter_by(
        is_admin=False
    ).count()
    total_missions = Mission.query.count()
    total_puzzles = Puzzle.query.count()
    total_completions = MissionCompletion.query.count()
    total_xp = db.session.query(
        db.func.coalesce(
            db.func.sum(MissionCompletion.xp_earned),
            0
        )
    ).scalar()
    mission_stats = []
    missions = Mission.query.order_by(
        Mission.id.asc()
    ).all()
    for mission in missions:
        completed = MissionCompletion.query.filter_by(
            mission_id=mission.id
        ).count()
        puzzle_count = Puzzle.query.filter_by(
            mission_id=mission.id
        ).count()
        mission_stats.append({
            "mission": mission,
            "completed": completed,
            "puzzles": puzzle_count
        })
    top_agents = User.query.filter_by(
        is_admin=False
    ).order_by(
        User.xp.desc()
    ).limit(5).all()

    return render_template(
        "admin/analytics.html",
        total_agents=total_agents,
        total_missions=total_missions,
        total_puzzles=total_puzzles,
        total_completions=total_completions,
        total_xp=total_xp,
        mission_stats=mission_stats,
        top_agents=top_agents
    )

@admin_bp.route("/settings", methods=["GET", "POST"])
@login_required
def settings():

    if not current_user.is_admin:
        return "Access Denied", 403
    if request.method == "POST":
        flash(
            "Settings updated successfully! ⚙️",
            "success"
        )
        return redirect(
            url_for("admin.settings")
        )
    return render_template(
        "admin/settings.html"
    )