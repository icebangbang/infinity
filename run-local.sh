docker build  -f ./CerelyScheduleDockerfile -t dao-celery-schedule:latest .

docker stop  dao-celery-schedule-1
docker run -d --privileged=true  -e "index=1"  -e "FLASK_ENV=test" --name=dao-celery-schedule-1  --net=host --rm -it dao-celery-schedule:latest

docker build -f ./Dockerfile -t dao:latest .
echo '##################################'
docker stop dao
docker run -d --privileged=true -v /var/log/dao:/var/log/dao -e "profiles=test" --name=dao -e "index=1" -e "port=20500" --net=host --rm -it dao:latest
echo '##################################'

docker build --no-cache -f ./CerelyDockerfile -t dao-celery:latest .

for ((index1=1; index1<=1; index1++))
do
echo ${index1}
docker stop dao-celery-${index1}
docker run -d --privileged=true  -e "profiles=test" --name=dao-celery-${index1} -e "index=${index1}" -e "route=default" -e "FLASK_ENV=test" -e "thread=50" --net=host --rm -it dao-celery:latest
done

for ((index2=2; index2<=5; index2++))
do
echo ${index2}
docker stop dao-celery-${index2}
docker run -d --privileged=true  -e "profiles=test" --name=dao-celery-${index2} -e "index=${index2}" -e "route=day_level" -e "FLASK_ENV=test" -e "thread=50" --net=host --rm -it dao-celery:latest
done

for ((index3=6; index3<=11; index3++))
do
echo ${index3}
docker stop dao-celery-${index3}
echo "shutdown dao-celery-${index3}"
docker run -d --privileged=true  -e "profiles=test" --name=dao-celery-${index3} -e "index=${index3}" -e "route=indicator" -e "FLASK_ENV=test" -e "thread=20" --net=host --rm -it dao-celery:latest
done