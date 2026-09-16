from flask import Blueprint, render_template, redirect, request, url_for, flash
from flask_login import login_required, current_user
from app.models import Puzzle, User,MissionCompletion, PuzzleProgress
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/dashboard")
@login_required
def dashboard():

    return render_template(
        "dashboard.html",
        user=current_user
    )

@dashboard_bp.route("/puzzle-vault")
@login_required
def puzzle_vault():

    puzzles = Puzzle.query.order_by(
        Puzzle.mission_id.asc(),
        Puzzle.order.asc()
    ).all()
    progress = PuzzleProgress.query.filter_by(
        user_id=current_user.id
    ).all()
    completed_puzzle_ids = {
        p.puzzle_id
        for p in progress
        if p.completed
    }
    return render_template(
        "puzzle_vault.html",
        puzzles=puzzles,
        completed_puzzle_ids=completed_puzzle_ids
    )

@dashboard_bp.route("/achievements")
@login_required
def achievements():

    missions_completed = current_user.missions_completed or 0
    badges_count = current_user.badges or 0
    xp = current_user.xp or 0

    achievements = [
        {
            "icon": "🕵️",
            "title": "Rookie Agent",
            "description": "Join Project Cipher and begin your investigation.",
            "requirement": "Create your agent profile",
            "unlocked": True
        },
        {
            "icon": "🧩",
            "title": "First Crack",
            "description": "Solve your very first puzzle.",
            "requirement": "Solve 1 puzzle",
            "unlocked": xp > 0
        },
        {
            "icon": "🔍",
            "title": "Cipher Breaker",
            "description": "Complete your first mission.",
            "requirement": "Complete 1 mission",
            "unlocked": missions_completed >= 1
        },
        {
            "icon": "🎯",
            "title": "Field Agent",
            "description": "Complete multiple investigations.",
            "requirement": "Complete 3 missions",
            "unlocked": missions_completed >= 3
        },
        {
            "icon": "🏆",
            "title": "Master Investigator",
            "description": "Become one of Project Cipher's elite agents.",
            "requirement": "Complete 5 missions",
            "unlocked": missions_completed >= 5
        },
        {
            "icon": "⚡",
            "title": "XP Hunter",
            "description": "Earn a large amount of experience.",
            "requirement": "Earn 1000 XP",
            "unlocked": xp >= 1000
        }
    ]

    unlocked_count = sum(
        1 for achievement in achievements
        if achievement["unlocked"]
    )

    return render_template(
        "achievements.html",
        achievements=achievements,
        unlocked_count=unlocked_count,
        total_count=len(achievements)
    )

@dashboard_bp.route("/profile")
@login_required
def profile():

    total_puzzles = Puzzle.query.count()

    solved_puzzles = PuzzleProgress.query.filter_by(
        user_id=current_user.id,
        completed=True
    ).count()

    return render_template(
        "profile.html",
        total_puzzles=total_puzzles,
        solved_puzzles=solved_puzzles
    )

@dashboard_bp.route("/settings", methods=["GET", "POST"])
@login_required
def settings():

    if request.method == "POST":

        action = request.form.get("action")
        if action == "profile":
            username = request.form.get(
                "username",
                ""
            ).strip()
            email = request.form.get(
                "email",
                ""
            ).strip()
            if not username or not email:
                flash(
                    "Username and email are required.",
                    "danger"
                )
                return redirect(
                    url_for("dashboard.settings")
                )
            existing_user = User.query.filter(
                User.email == email,
                User.id != current_user.id
            ).first()

            if existing_user:

                flash(
                    "This email is already registered.",
                    "danger"
                )
                return redirect(
                    url_for("dashboard.settings")
                )
            current_user.username = username
            current_user.email = email
            db.session.commit()
            flash(
                "Profile updated successfully! ✅",
                "success"
            )
            return redirect(
                url_for("dashboard.settings")
            )

        elif action == "password":
            current_password = request.form.get(
                "current_password",
                ""
            )
            new_password = request.form.get(
                "new_password",
                ""
            )
            confirm_password = request.form.get(
                "confirm_password",
                ""
            )
            if not current_password or not new_password:
                flash(
                    "Please fill all password fields.",
                    "danger"
                )
                return redirect(
                    url_for("dashboard.settings")
                )
            if not check_password_hash(
                current_user.password,
                current_password
            ):
                flash(
                    "Current password is incorrect.",
                    "danger"
                )
                return redirect(
                    url_for("dashboard.settings")
                )
            if len(new_password) < 6:
                flash(
                    "New password must contain at least 6 characters.",
                    "danger"
                )
                return redirect(
                    url_for("dashboard.settings")
                )
            if new_password != confirm_password:
                flash(
                    "New passwords do not match.",
                    "danger"
                )
                return redirect(
                    url_for("dashboard.settings")
                )
            current_user.password = generate_password_hash(
                new_password
            )
            db.session.commit()
            flash(
                "Password changed successfully! 🔐",
                "success"
            )
            return redirect(
                url_for("dashboard.settings")
            )
    return render_template(
        "settings.html"
    )

@dashboard_bp.route("/leaderboard")
@login_required
def leaderboard():

    agents = User.query.filter_by(
        is_admin=False
    ).order_by(
        User.xp.desc(),
        User.missions_completed.desc(),
        User.badges.desc()
    ).all()

    return render_template(
        "leaderboard.html",
        agents=agents
    )