from flask import Blueprint

rest = Blueprint('op', __name__,url_prefix='/api/indicator')



# def init_all_blueprint(app):
#     app.register_blueprint(rest)
#     app.register_blueprint(auth)
#     app.register_blueprint(tr)


from . import indicator
