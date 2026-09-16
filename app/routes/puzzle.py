from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required
from app.extensions import db
from app.utils import calculate_level, calculate_rank
from app.models import Mission, Puzzle, PuzzleProgress, MissionCompletion
from datetime import datetime, timedelta


puzzle_bp = Blueprint(
    "puzzle",
    __name__
)


@puzzle_bp.route("/puzzle/<int:id>", methods=["GET", "POST"])
@login_required
def solve_puzzle(id):

    puzzle = Puzzle.query.get_or_404(id)
    mission = Mission.query.get_or_404(puzzle.mission_id)

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
            attempts_remaining=puzzle.max_attempts,
            retry_count=0,
            completed=False,
            reset_available_at=None
        )

        db.session.add(progress)
        db.session.commit()

    if progress.completed:
        flash(
            "✅ You have already completed this puzzle.",
            "info"
        )
        return redirect(
            url_for(
                "mission.mission_detail",
                mission_id=mission.id
            )
        )

    now = datetime.utcnow()
    if (
        progress.attempts_remaining <= 0
        and progress.reset_available_at
    ):

        if now >= progress.reset_available_at:
            progress.attempts_remaining = 3
            progress.reset_available_at = None
            db.session.commit()
            flash(
                "🔓 3 attempts restored! "
                "Good luck, Agent.",
                "success"
            )
        else:
            remaining = (progress.reset_available_at - now)
            minutes = int(remaining.total_seconds() // 60)
            seconds = int(remaining.total_seconds() % 60)
            return render_template(
                "puzzle.html",
                mission=mission,
                puzzle=puzzle,
                progress=progress,
                cooldown_minutes=minutes,
                cooldown_seconds=seconds
            )

    if request.method == "POST":
        if progress.attempts_remaining <= 0:
            flash(
                "🔒 No attempts remaining.",
                "danger"
            )
            return redirect(
                url_for(
                    "puzzle.solve_puzzle",
                    id=puzzle.id
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
            current_user.xp += puzzle.reward_xp
            current_user.level = calculate_level(current_user.xp)
            current_user.rank = calculate_rank(current_user.level)
            db.session.commit()

            puzzles = Puzzle.query.filter_by(
                mission_id=mission.id
            ).order_by(
                Puzzle.order.asc()
            ).all()
            current_index = puzzles.index(puzzle)

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
                    current_user.xp += mission.reward_xp
                    current_user.missions_completed += 1
                    current_user.level = calculate_level(current_user.xp)
                    current_user.rank = calculate_rank(current_user.level)
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
                f"✅ Correct! "
                f"+{puzzle.reward_xp} XP. "
                f"Next puzzle unlocked! 🔓",
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

        if progress.attempts_remaining <= 0:
            progress.attempts_remaining = 0
            progress.reset_available_at = (
                datetime.utcnow()
                + timedelta(minutes=15)
            )
            flash(
                "🔒 All 3 attempts used! "
                "You can wait 15 minutes for a free reset.",
                "danger"
            )
        else:
            flash(
                f"❌ Wrong Answer! "
                f"{progress.attempts_remaining} "
                f"attempt(s) remaining.",
                "danger"
            )
        db.session.commit()

    return render_template(
        "puzzle.html",
        mission=mission,
        puzzle=puzzle,
        progress=progress
    )


@puzzle_bp.route("/puzzle/<int:puzzle_id>/reset", methods=["POST"])
@login_required
def reset_attempts(puzzle_id):

    puzzle = Puzzle.query.get_or_404(puzzle_id)
    mission = Mission.query.get_or_404(puzzle.mission_id)
    progress = PuzzleProgress.query.filter_by(
        user_id=current_user.id,
        mission_id=mission.id,
        puzzle_id=puzzle.id
    ).first()

    if not progress:
        flash(
            "Puzzle progress not found.",
            "danger"
        )
        return redirect(
            url_for(
                "mission.mission_detail",
                mission_id=mission.id
            )
        )

    if progress.completed:
        flash(
            "Puzzle already completed.",
            "info"
        )
        return redirect(
            url_for(
                "mission.solve_puzzle",
                mission_id=mission.id,
                puzzle_id=puzzle.id
            )
        )

    if progress.attempts_remaining > 0:
        flash(
            "You still have attempts remaining.",
            "warning"
        )
        return redirect(
            url_for(
                "mission.solve_puzzle",
                mission_id=mission.id,
                puzzle_id=puzzle.id
            )
        )
    now = datetime.utcnow()

    if progress.reset_available_at is None:
        progress.reset_available_at = (
            now + timedelta(minutes=15)
        )
        db.session.commit()
        flash(
            "⏳ Reset started! "
            "You will receive 3 attempts after 15 minutes.",
            "info"
        )
        return redirect(
            url_for(
                "mission.solve_puzzle",
                mission_id=mission.id,
                puzzle_id=puzzle.id
            )
        )

    if now < progress.reset_available_at:

        remaining = (progress.reset_available_at - now)
        minutes = int(remaining.total_seconds() // 60)
        seconds = int(remaining.total_seconds() % 60)
        flash(
            f"⏳ Please wait "
            f"{minutes:02d}:{seconds:02d}.",
            "warning"
        )
        return redirect(
            url_for(
                "mission.solve_puzzle",
                mission_id=mission.id,
                puzzle_id=puzzle.id
            )
        )
    progress.attempts_remaining = 3
    progress.reset_available_at = None
    db.session.commit()
    flash(
        "🔓 Attempts restored! "
        "You received 3 new attempts.",
        "success"
    )
    return redirect(
        url_for(
            "mission.solve_puzzle",
            mission_id=mission.id,
            puzzle_id=puzzle.id
        )
    )