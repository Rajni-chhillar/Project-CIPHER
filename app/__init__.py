from flask import Flask, render_template
from .extensions import db
from .extensions import bcrypt
from .extensions import login_manager
from .models import User

def create_app():
    app = Flask(__name__)

    app.config.from_object("config.Config")

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    login_manager.login_view = "auth.login"

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from .routes.main import main_bp
    from .routes.auth import auth_bp
    from .routes.dashboard import dashboard_bp
    from .routes.mission import mission_bp
    from .routes.admin import admin_bp
    from .routes.puzzle import puzzle_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(mission_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(puzzle_bp)

    @app.errorhandler(404)
    def page_not_found(error):

        return render_template(
            "404.html"
        ),404

    @app.errorhandler(500)
    def internal_error(error):

        return render_template(
            "500.html"
        ),500

    with app.app_context():
        db.create_all()
    return app