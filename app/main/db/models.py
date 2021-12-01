from flask_sqlalchemy import SQLAlchemy
from app.main.utils.timezone import change_timezone

db = SQLAlchemy(session_options={'autocommit': True})


# db = SQLAlchemy()
class TableBase:
    __table_args__ = {"useexisting": True}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    is_deleted = db.Column(db.CHAR, nullable=False, default=0)
    create_date = db.Column(db.DATETIME, nullable=True, default=change_timezone())
    modify_date = db.Column(db.DATETIME, nullable=True, default=change_timezone())



def init_db(app):
    db.init_app(app)