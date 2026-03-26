from flask import Flask
from dotenv import load_dotenv

from config import DevelopmentConfig

from .admin.routes import admin_bp
from .advisor.routes import advisor_bp
from .auth.routes import auth_bp
from .bibliographic_search.routes import bibliographic_search_bp
from .cli import register_commands
from .extensions import db, login_manager
from .main.routes import main_bp
from .methodology.routes import methodology_bp
from .projects.routes import projects_bp
from .references.routes import references_bp
from .reports.routes import reports_bp


def create_app(config_class=DevelopmentConfig):
    load_dotenv()
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)

    from .models import domain  # noqa: F401
    from .models import load_user  # noqa: F401

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(methodology_bp)
    app.register_blueprint(references_bp)
    app.register_blueprint(bibliographic_search_bp)
    app.register_blueprint(advisor_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(reports_bp)

    register_commands(app)

    @app.context_processor
    def inject_shell():
        return {
            "app_name": app.config["APP_NAME"],
            "institution_name": app.config["INSTITUTION_NAME"],
        }

    return app
