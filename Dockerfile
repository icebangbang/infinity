FROM python:3.8.10-slim

RUN  sed -i s@/archive.ubuntu.com/@/mirrors.aliyun.com/@g /etc/apt/sources.list
RUN  sed -i s@/deb.debian.org/@/mirrors.aliyun.com/@g /etc/apt/sources.list
RUN  apt-get clean

WORKDIR /
COPY ./requirements.txt /

#RUN sed -i "s/deb.debian.org/mirrors.aliyun.com/g" /etc/apt/sources.list
#RUN sed -i "s/security.debian.org/mirrors.aliyun.com/g" /etc/apt/sources.list
##
#RUN echo " \
#[global] \n \
#timeout = 5000 \n \
#index-url = http://pypi.douban.com/simple \n \
#trusted-host = pypi.douban.com \n \
#" > /etc/pip.conf


#RUN pip3 install --user -i  https://mirrors.aliyun.com/pypi/simple  -r requirements.txt
RUN pip3 install --trusted-host mirrors.cloud.aliyuncs.com -i https://mirrors.cloud.aliyuncs.com/pypi/simple --no-cache-dir -r requirements.txt


COPY ./app /app
COPY ./manage.py /
COPY ./config.py /
COPY ./celeryconfig.py /
COPY ./celeryconfig_offline.py /

RUN mkdir /var/log/dao



# CMD cd /app && flask run --host=0.0.0.0 --port=${port} --with-threads --no-debugger --no-reload
#CMD  gunicorn -k gevent -w 4 -b 0.0.0.0:${port} app.run:app -e FLASK_ENV=${profiles}
#gunicorn -k gevent -w 4 -b 0.0.0.0:20011 app.run:app -e FLASK_ENV=default
#CMD celery -A manage.celery worker -l info -P  gevent -Q ${route} -c 50 -n worker${index}.%h

CMD  gunicorn -c app/gunicorn/gun.py --log-config app/gunicorn/gunicorn_logging.conf -b 0.0.0.0:${port} manage:app -e FLASK_ENV=${profiles}

# gunicorn -c app/gunicorn/gun.py --log-config app/gunicorn/gunicorn_logging.conf -b 0.0.0.0:20050 manage:app -e FLASK_ENV=test