docker build  -f ./CerelyScheduleDockerfile -t dao-celery-schedule:latest .

docker stop  dao-celery-schedule-1
docker run -d --privileged=true  -e "index=1"  -e "FLASK_ENV=test" --name=dao-celery-schedule-1  --net=host --rm -it dao-celery-schedule:latest

docker build -f ./Dockerfile -t dao:latest .
echo '##################################'
docker stop dao sleep 5
docker run -d --privileged=true -v /var/log/dao:/var/log/dao -e "profiles=test" --name=dao -e "index=1" -e "port=20500" --net=host --rm -it dao:latest
echo '##################################'

docker build --no-cache -f ./CerelyDockerfile -t dao-celery:latest .

docker stop dao-celery-1
docker run -d --privileged=true  -e "profiles=test" --name=dao-celery-1 -e "index=${1}" -e "route=default" -e "FLASK_ENV=test" -e "thread=50" --net=host --rm -it dao-celery:latest

docker stop dao-celery-2
docker run -d --privileged=true  -e "profiles=test" --name=dao-celery-2 -e "index=${2}" -e "route=day_level" -e "FLASK_ENV=test" -e "thread=50" --net=host --rm -it dao-celery:latest

docker stop dao-celery-3
docker run -d --privileged=true  -e "profiles=test" --name=dao-celery-3 -e "index=${3}" -e "route=day_level" -e "FLASK_ENV=test" -e "thread=50" --net=host --rm -it dao-celery:latest

docker stop dao-celery-4
docker run -d --privileged=true  -e "profiles=test" --name=dao-celery-4 -e "index=${4}" -e "route=day_level" -e "FLASK_ENV=test" -e "thread=50" --net=host --rm -it dao-celery:latest

docker stop dao-celery-5
docker run -d --privileged=true  -e "profiles=test" --name=dao-celery-5 -e "index=${4}" -e "route=day_level" -e "FLASK_ENV=test" -e "thread=50" --net=host --rm -it dao-celery:latest


for ((index3=6; index3<=11; index3++))
do
echo ${index3}
docker stop dao-celery-${index3}

echo "shutdown dao-celery-${index3}"
docker run -d --privileged=true  -e "profiles=test" --name=dao-celery-${index3} -e "index=${index3}" -e "route=indicator" -e "FLASK_ENV=test" -e "thread=20" --net=host --rm -it dao-celery:latest
done