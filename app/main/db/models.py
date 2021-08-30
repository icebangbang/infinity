from flask_sqlalchemy import SQLAlchemy
from app.main.utils.timezone import change_timezone

db = SQLAlchemy(session_options={'autocommit': True})


# db = SQLAlchemy()


def init_db(app):
    db.init_app(app)