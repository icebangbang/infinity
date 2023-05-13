## 在目标服务器中执行用
# bash run-dao-local.sh infinity

PIP_MIRROR=http://127.0.0.1:7104/root/pypi/+simple/
PIP_MIRROR_HOST=127.0.0.1:7104

env=${1}


docker stop dao
docker build --network=host --build-arg PIP_MIRROR=${PIP_MIRROR} --build-arg PIP_MIRROR_HOST=${PIP_MIRROR_HOST} -f ./Dockerfile -t dao:latest .
docker run -d --privileged=true -v /var/log/dao:/var/log/dao -e "profiles=${env}" --name=dao -e "index=1" -e "port=20500" -v /etc/localtime:/etc/localtime:ro -p 20500:20500 --rm -it dao:latest
#docker build --network=host --build-arg PIP_MIRROR=http://127.0.0.1:7104/root/pypi/+simple/ --build-arg PIP_MIRROR_HOST=127.0.0.1:7104 -f ./Dockerfile -t dao:latest .
#docker run -d --privileged=true -v /var/log/dao:/var/log/dao -e "profiles=infinity" --name=dao -e "index=1" -e "port=20500" -v /etc/localtime:/etc/localtime:ro --net=host --rm -it dao:latest


echo y | docker system prune