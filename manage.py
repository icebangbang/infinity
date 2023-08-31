from app import application
import os

# 获取环境变量,
# pycharm启动可以在 RUN/DEBUG Configuration-Environment variables中添加FLASK_ENV
# PYTHONUNBUFFERED=1;FLASK_ENV=infinityLocal;SERVER_PORT=20058
#
env = os.environ.get('FLASK_ENV') or 'infinity'
app = application.create_app_v2(env,NACOS_ENABLE = os.environ.get('NACOS_ENABLE'))  # from .main.rest import rest as main_blueprint


from app.celery_application import celery


if __name__ == '__main__':
    port = os.environ.get('SERVER_PORT') or 20060
    app.flask.run(host='0.0.0.0', port=port, debug=True, use_reloader=False, threaded=True)
