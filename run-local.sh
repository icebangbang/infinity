# sh run-local.sh  deveploment  4

env=${1}
num=${2}


project=dao-celery
version=latest

docker build --no-cache -f ./CerelyDockerfile -t ${project}:${version} .

#docker build -f ./CerelyDockerfile -t ${project}:${version} .


for ((index=1; index<=num; index++))
do

docker stop ${project}-${index}
docker run -d --privileged=true  --name=${project}-${index} -e "index=${index}" --net=host --rm -it ${project}:${version}

done

docker rmi $(docker images | grep "none" | awk '{print $3}')