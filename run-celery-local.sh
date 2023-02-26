# bash run-celery-local.sh  infinity 1 default
# 本地启动

env=${1}
num=${2}
route=${3}

project=dao-celery
version=latest

PIP_MIRROR=http://127.0.0.1:7104/root/pypi/+simple/
PIP_MIRROR_HOST=127.0.0.1:7104

docker build --network=host --build-arg PIP_MIRROR=${PIP_MIRROR} --build-arg PIP_MIRROR_HOST=${PIP_MIRROR_HOST} -f ./CerelyDockerfile -t dao-celery:latest .

#docker build --no-cache -f ./CerelyDockerfile -t ${project}:${version} .
#docker build -f ./CerelyDockerfile -t ${project}:${version} .


for ((index=1; index<=num; index++))
do

docker stop ${project}-${index}
echo "docker run --privileged=true  --name=${project}-${index} -e "index=${index}" -e "route=${route}" -e "thread=50" --net=host --rm -it ${project}:${version}"
docker run -d --privileged=true  --name=${project}-${index} -e "index=${index}" -e "route=${route}" -e "thread=50" --net=host --rm -it ${project}:${version}

done

docker run  --privileged=true  --name=dao-celery-1 -e index=1 -e route=default -e thread=50 --net=host --rm -it dao-celery:latest

echo y | docker system prune
#docker rmi $(docker images | grep "none" | awk '{print $3}')