from flask import Flask
from flask_jwt_extended import JWTManager
from .config import Config
from .models.user import db as user_db
from .models.ticket import db as ticket_db
from .models.sla_tracker import db as sla_db
from .models.escalation_event import db as event_db
from .routes.tickets import tickets_bp
from .routes.auth import auth_bp


def create_app(config: type = Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config)

    for db in [user_db, ticket_db, sla_db, event_db]:
        db.init_app(app)

    JWTManager(app)

    app.register_blueprint(tickets_bp)
    app.register_blueprint(auth_bp)

    with app.app_context():
        db = user_db
        db.create_all()

    return app
