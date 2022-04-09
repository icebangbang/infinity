docker build  -f ./CerelyScheduleDockerfile -t dao-celery-schedule:latest .

docker stop  dao-celery-schedule-1
docker run -d --privileged=true  -e "index=1"  -e "FLASK_ENV=test" --name=dao-celery-schedule-1  --net=host --rm -it dao-celery-schedule:latest

docker build -f ./Dockerfile -t dao:latest .
docker stop dao
docker run -d --privileged=true -v /var/log/dao:/var/log/dao -e "profiles=test" --name=dao -e "index=1" -e "port=20500" --net=host --rm -it dao:latest

docker build --no-cache -f ./CerelyDockerfile -t dao-celery:latest .

for ((index=1; index<=1; index++))
do
docker stop dao-celery-${index}
docker run -d --privileged=true  -e "profiles=test" --name=dao-celery-${index} -e "index=${index}" -e "route=default" -e "FLASK_ENV=test" -e "thread=50" --net=host --rm -it dao-celery:latest
echo ${index}
done

for ((index=2; index<=5; index++))
do
docker stop dao-celery-${index}
docker run -d --privileged=true  -e "profiles=test" --name=dao-celery-${index} -e "index=${index}" -e "route=day_level" -e "FLASK_ENV=test" -e "thread=50" --net=host --rm -it dao-celery:latest
echo ${index}
done

for ((index=6; index<=11; index++))
do
docker stop dao-celery-${index}
docker run -d --privileged=true  -e "profiles=test" --name=dao-celery-${index} -e "index=${index}" -e "route=indicator" -e "FLASK_ENV=test" -e "thread=20" --net=host --rm -it dao-celery:latest
echo ${index}
done