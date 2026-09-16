from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from app.models import Mission,Puzzle, PuzzleProgress, MissionCompletion
from app.extensions import db
from datetime import datetime, timedelta


mission_bp = Blueprint(
    "mission",
    __name__
)

@mission_bp.route("/missions")
@login_required
def missions():

    if current_user.is_admin:
        return redirect(
            url_for("admin.dashboard")
        )
    missions = Mission.query.order_by(
        Mission.id.asc()
    ).all()

    mission_status = {}

    for mission in missions:
        completion = MissionCompletion.query.filter_by(
            user_id=current_user.id,
            mission_id=mission.id
        ).first()

        if completion:
            mission_status[mission.id] = "completed"
        elif mission.id == 1:
            mission_status[mission.id] = "unlocked"
        else:
            previous_completion = MissionCompletion.query.filter_by(
                user_id=current_user.id,
                mission_id=mission.id - 1
            ).first()
            if previous_completion:
                mission_status[mission.id] = "unlocked"
            else:
                mission_status[mission.id] = "locked"

    return render_template(
        "missions.html",
        missions=missions,
        mission_status=mission_status
    )

@mission_bp.route("/<int:mission_id>")
@login_required
def mission_detail(mission_id):

    mission = Mission.query.get_or_404(mission_id)
    puzzles = Puzzle.query.filter_by(
        mission_id=mission.id
    ).order_by(
        Puzzle.order.asc()
    ).all()


    if not puzzles:
        flash(
            "This mission does not have any puzzles yet.",
            "warning"
        )
        return redirect(
            url_for("mission.missions")
        )
    puzzle_status = {}

    for index, puzzle in enumerate(puzzles):
        progress = PuzzleProgress.query.filter_by(
            user_id=current_user.id,
            mission_id=mission.id,
            puzzle_id=puzzle.id
        ).first()

        if progress and progress.completed:
            puzzle_status[puzzle.id] = "completed"
        elif index == 0:
            puzzle_status[puzzle.id] = "available"
        else:
            previous_puzzle = puzzles[index - 1]
            previous_progress = PuzzleProgress.query.filter_by(
                user_id=current_user.id,
                mission_id=mission.id,
                puzzle_id=previous_puzzle.id
            ).first()
            if (
                previous_progress
                and previous_progress.completed
            ):
                puzzle_status[puzzle.id] = "available"
            else:
                puzzle_status[puzzle.id] = "locked"

    return render_template(
        "mission_detail.html",
        mission=mission,
        puzzles=puzzles,
        puzzle_status=puzzle_status
    )


@mission_bp.route("/<int:mission_id>/puzzle/<int:puzzle_id>", methods=["GET", "POST"])
@login_required
def solve_puzzle(mission_id, puzzle_id):

    if current_user.is_admin:
        return redirect(
            url_for("admin.dashboard")
        )
    mission = Mission.query.get_or_404(mission_id)

    if mission.id > 1:
        previous_completion = MissionCompletion.query.filter_by(
            user_id=current_user.id,
            mission_id=mission.id - 1
        ).first()

        if previous_completion is None:
            flash(
                "🔒 Complete the previous mission first.",
                "warning"
            )
            return redirect(
                url_for("mission.missions")
            )

    puzzle = Puzzle.query.filter_by(
        id=puzzle_id,
        mission_id=mission.id
    ).first_or_404()

    puzzles = Puzzle.query.filter_by(
        mission_id=mission.id
    ).order_by(
        Puzzle.order.asc()
    ).all()

    current_index = puzzles.index(puzzle)

    if current_index > 0:
        previous_puzzle = puzzles[
            current_index - 1
        ]
        previous_progress = PuzzleProgress.query.filter_by(
            user_id=current_user.id,
            mission_id=mission.id,
            puzzle_id=previous_puzzle.id
        ).first()

        if (
            not previous_progress
            or not previous_progress.completed
        ):
            flash(
                "🔒 Complete the previous puzzle first.",
                "warning"
            )
            return redirect(
                url_for(
                    "mission.solve_puzzle",
                    mission_id=mission.id,
                    puzzle_id=previous_puzzle.id
                )
            )

    progress = PuzzleProgress.query.filter_by(
        user_id=current_user.id,
        mission_id=mission.id,
        puzzle_id=puzzle.id
    ).first()

    if not progress:
        progress = PuzzleProgress(
            user_id=current_user.id,
            mission_id=mission.id,
            puzzle_id=puzzle.id,
            completed=False,
            attempts_remaining=3,
            retry_count=0,
            reset_available_at=None
        )

        db.session.add(progress)
        db.session.commit()

    now = datetime.utcnow()

    if (
        progress.attempts_remaining <= 0
        and progress.reset_available_at
        and not progress.completed
    ):
        
        if now >= progress.reset_available_at:
            progress.attempts_remaining = 3
            progress.reset_available_at = None
            db.session.commit()
            flash(
                "🔓 3 attempts restored! Good luck, Agent.",
                "success"
            )
        else:
            remaining = (
                progress.reset_available_at - now
            )
            total_seconds = int(
                remaining.total_seconds()
            )
            minutes = total_seconds // 60
            seconds = total_seconds % 60

            flash(
                f"⏳ New attempts available in "
                f"{minutes:02d}:{seconds:02d}.",
                "warning"
            )

    if request.method == "POST":
        if progress.completed:
            flash(
                "This puzzle is already completed.",
                "info"
            )
            return redirect(
                url_for(
                    "mission.solve_puzzle",
                    mission_id=mission.id,
                    puzzle_id=puzzle.id
                )
            )
        
        if progress.attempts_remaining <= 0:

            if (
                progress.reset_available_at
                and datetime.utcnow()
                >= progress.reset_available_at
            ):
                progress.attempts_remaining = 3
                progress.reset_available_at = None
                db.session.commit()
            else:
                flash(
                    "❌ You have no attempts left.",
                    "danger"
                )
                return redirect(
                    url_for(
                        "mission.solve_puzzle",
                        mission_id=mission.id,
                        puzzle_id=puzzle.id
                    )
                )

        user_answer = request.form.get(
            "answer",
            ""
        ).strip()
        if (
            user_answer.lower()
            == puzzle.answer.strip().lower()
        ):
            progress.completed = True
            progress.reset_available_at = None
            current_user.xp += puzzle.xp
            db.session.commit()

            if current_index == len(puzzles) - 1:
                existing_completion = (
                    MissionCompletion.query.filter_by(
                        user_id=current_user.id,
                        mission_id=mission.id
                    ).first()
                )

                if not existing_completion:
                    completion = MissionCompletion(
                        user_id=current_user.id,
                        mission_id=mission.id,
                        xp_earned=mission.reward_xp
                    )

                    db.session.add(completion)

                    current_user.xp += (mission.reward_xp)
                    current_user.missions_completed += 1
                    current_user.badges += 1
                    db.session.commit()
                flash(
                    f"🏆 Mission Completed! "
                    f"+{mission.reward_xp} XP",
                    "success"
                )
                return redirect(
                    url_for(
                        "mission.mission_detail",
                        mission_id=mission.id
                    )
                )

            next_puzzle = puzzles[current_index + 1]

            flash(
                f"✅ Correct! +{puzzle.xp} XP. "
                f"Next puzzle unlocked!",
                "success"
            )
            return redirect(
                url_for(
                    "mission.solve_puzzle",
                    mission_id=mission.id,
                    puzzle_id=next_puzzle.id
                )
            )
        progress.attempts_remaining -= 1
        if progress.attempts_remaining < 0:
            progress.attempts_remaining = 0
        if progress.attempts_remaining == 0:
            progress.reset_available_at = (
                datetime.utcnow()
                + timedelta(minutes=15)
            )
            db.session.commit()
            flash(
                "🔒 All 3 attempts used! "
                "You can purchase 3 more attempts using XP "
                "or wait 15 minutes for a free reset.",
                "danger"
            )
        else:
            db.session.commit()
            flash(
                f"❌ Incorrect answer. "
                f"{progress.attempts_remaining} "
                f"attempts remaining.",
                "danger"
            )
        return redirect(
            url_for(
                "mission.solve_puzzle",
                mission_id=mission.id,
                puzzle_id=puzzle.id
            )
        )
    return render_template(
        "puzzle.html",
        mission=mission,
        puzzle=puzzle,
        progress=progress
    )


@mission_bp.route("/mission/<int:mission_id>/puzzle/<int:puzzle_id>/buy-attempts",methods=["POST"])
@login_required
def buy_attempts(mission_id, puzzle_id):

    mission = Mission.query.get_or_404(mission_id)
    puzzle = Puzzle.query.filter_by(
        id=puzzle_id,
        mission_id=mission.id
    ).first_or_404()

    progress = PuzzleProgress.query.filter_by(
        user_id=current_user.id,
        mission_id=mission_id,
        puzzle_id=puzzle_id
    ).first()

    if not progress:
        flash(
            "Puzzle progress not found.",
            "danger"
        )
        return redirect(
            url_for(
                "mission.solve_puzzle",
                mission_id=mission_id,
                puzzle_id=puzzle_id
            )
        )

    if progress.completed:
        flash(
            "This puzzle is already completed.",
            "info"
        )
        return redirect(
            url_for(
                "mission.solve_puzzle",
                mission_id=mission_id,
                puzzle_id=puzzle_id
            )
        )

    retry_costs = [50,75,100,150]
    if progress.retry_count < len(
        retry_costs
    ):
        cost = retry_costs[progress.retry_count]
    else:
        cost = 150

    if current_user.xp < cost:
        flash(
            f"Not enough XP! "
            f"You need {cost} XP.",
            "danger"
        )
        return redirect(
            url_for(
                "mission.solve_puzzle",
                mission_id=mission_id,
                puzzle_id=puzzle_id
            )
        )
    current_user.xp -= cost
    progress.attempts_remaining += 3
    progress.retry_count += 1
    progress.reset_available_at = None
    db.session.commit()

    flash(
        f"🔓 3 attempts unlocked! "
        f"-{cost} XP",
        "success"
    )
    return redirect(
        url_for(
            "mission.solve_puzzle",
            mission_id=mission_id,
            puzzle_id=puzzle_id
        )
    )