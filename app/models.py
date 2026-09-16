from datetime import datetime
from flask_login import UserMixin
from .extensions import db

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(100),nullable=False)
    email = db.Column(db.String(120),unique=True,nullable=False)
    password = db.Column(db.String(255),nullable=False)
    is_admin = db.Column(db.Boolean,default=False)
    created_at = db.Column(db.DateTime,default=datetime.utcnow)
    xp=db.Column(db.Integer,default=0)
    level=db.Column(db.Integer,default=1)
    rank = db.Column(db.String(50), default="Rookie Agent")
    missions_completed=db.Column(db.Integer, default=0)
    badges=db.Column(db.Integer,default=0)

    def __repr__(self):
        return f"<User {self.username}>"

class Mission(db.Model):
    __tablename__ ="missions"
    id=db.Column(db.Integer, primary_key=True)
    title=db.Column(db.String(150),nullable=False)
    description = db.Column(db.Text,nullable=False)
    difficulty = db.Column(db.String(50),default="Easy")
    reward_xp = db.Column(db.Integer,default=100)
    is_locked = db.Column(db.Boolean,default=True)
    created_at = db.Column(db.DateTime,default=datetime.utcnow)

    puzzles = db.relationship("Puzzle",backref="mission",lazy=True,cascade="all, delete-orphan",order_by="Puzzle.order")

    def __repr__(self):
        return f"<Mission {self.title}>"


class Puzzle(db.Model):
    __tablename__ = "puzzles"
    id = db.Column(db.Integer,primary_key=True)
    mission_id = db.Column(db.Integer,db.ForeignKey("missions.id"),nullable=False)
    title = db.Column(db.String(200),nullable=False)
    description = db.Column(db.Text,nullable=False)
    clue = db.Column(db.Text,nullable=True)
    question = db.Column(db.Text,nullable=False)
    answer = db.Column(db.String(200),nullable=False)
    image = db.Column(db.String(300),nullable=True)
    order = db.Column(db.Integer,nullable=False,default=1)
    xp = db.Column(db.Integer,default=100)
    max_attempts = db.Column(db.Integer,default=3)
    created_at = db.Column(db.DateTime,default=datetime.utcnow)

class PuzzleProgress(db.Model):
    __tablename__ = "puzzle_progress"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey("users.id"),nullable=False)
    mission_id = db.Column(db.Integer,nullable=False)
    puzzle_id = db.Column(db.Integer,nullable=False)
    completed = db.Column(db.Boolean,default=False)
    attempts_remaining = db.Column(db.Integer,default=0, nullable=False)
    retry_count = db.Column(db.Integer, default=0, nullable=False)
    reset_available_at = db.Column(db.DateTime,nullable=True)
    __table_args__ = (
        db.UniqueConstraint(
            "user_id",
            "mission_id",
            "puzzle_id",
            name="unique_user_puzzle"
        ),
    )

class MissionCompletion(db.Model):
    __tablename__ = "mission_completions"
    id = db.Column(db.Integer,primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey("users.id"),nullable=False)
    mission_id = db.Column(db.Integer,nullable=False)
    completed_at = db.Column(db.DateTime,default=datetime.utcnow)
    xp_earned = db.Column(db.Integer,default=0)
    __table_args__ = (
        db.UniqueConstraint(
            "user_id",
            "mission_id",
            name="unique_user_mission_completion"
        ),
    )

