## 在目标服务器中执行用

PIP_MIRROR=http://127.0.0.1:7104/root/pypi/+simple/
PIP_MIRROR_HOST=127.0.0.1:7104

env=${1}
docker stop  dao-celery-schedule-1
#docker build  -f ./CerelyScheduleDockerfile -t dao-celery-schedule:latest .
docker build --network=host --build-arg PIP_MIRROR=${PIP_MIRROR} --build-arg PIP_MIRROR_HOST=${PIP_MIRROR_HOST} -f ./CerelyScheduleDockerfile -t dao-celery-schedule:latest .

docker run -d --privileged=true  -e "index=1"  -e "FLASK_ENV=${env}" --name=dao-celery-schedule-1  --net=host --rm -it dao-celery-schedule:latest
#docker run --privileged=true  -e "index=1"  -e "FLASK_ENV=offline" --name=dao-celery-schedule-1  --net=host --rm -it dao-celery-schedule:latest


docker stop dao
docker build --network=host --build-arg PIP_MIRROR=${PIP_MIRROR} --build-arg PIP_MIRROR_HOST=${PIP_MIRROR_HOST} -f ./Dockerfile -t dao:latest .
#docker build --network=host --build-arg PIP_MIRROR=http://127.0.0.1:7104/root/pypi/+simple/ --build-arg PIP_MIRROR_HOST=127.0.0.1:7104 -f ./Dockerfile -t dao:latest .
docker run -d --privileged=true -v /var/log/dao:/var/log/dao -e "profiles=${env}" --name=dao -e "index=1" -e "port=20500" -v /etc/localtime:/etc/localtime:ro --net=host --rm -it dao:latest
#docker run -d --privileged=true -v /var/log/dao:/var/log/dao -e "profiles=infinity" --name=dao -e "index=1" -e "port=20500" -v /etc/localtime:/etc/localtime:ro --net=host --rm -it dao:latest



for ((index1=1; index1<=1; index1++))
do
echo ${index1}
docker stop dao-celery-${index1}
done

for ((index2=2; index2<=5; index2++))
do
echo ${index2}
docker stop dao-celery-${index2}
done

for ((index3=6; index3<=20; index3++))
do
echo ${index3}
docker stop dao-celery-${index3}
done

docker build --network=host --build-arg PIP_MIRROR=${PIP_MIRROR} --build-arg PIP_MIRROR_HOST=${PIP_MIRROR_HOST} -f ./CerelyDockerfile -t dao-celery:latest .

for ((index1=1; index1<=1; index1++))
do
docker run -d --privileged=true  -e "profiles=${env}" --name=dao-celery-${index1} -e "index=${index1}" -e "route=default" -e "FLASK_ENV=${env}" -e "thread=50" -v /etc/localtime:/etc/localtime:ro --net=host --rm -it dao-celery:latest
done

for ((index2=2; index2<=6; index2++))
do
docker run -d --privileged=true  -e "profiles=${env}" --name=dao-celery-${index2} -e "index=${index2}" -e "route=day_level" -e "FLASK_ENV=${env}" -e "thread=50" -v /etc/localtime:/etc/localtime:ro --net=host --rm -it dao-celery:latest
done

for ((index3=7; index3<=17; index3++))
do
docker run -d --privileged=true  -e "profiles=${env}" --name=dao-celery-${index3} -e "index=${index3}" -e "route=indicator" -e "FLASK_ENV=${env}" -e "thread=20" -v /etc/localtime:/etc/localtime:ro --net=host --rm -it dao-celery:latest
done

echo y | docker system prune