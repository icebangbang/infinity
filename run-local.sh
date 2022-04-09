docker build  -f ./CerelyScheduleDockerfile -t dao-celery-schedule:latest .

docker stop  dao-celery-schedule-1
docker run -d --privileged=true  -e "index=1"  -e "FLASK_ENV=test" --name=dao-celery-schedule-1  --net=host --rm -it dao-celery-schedule:latest