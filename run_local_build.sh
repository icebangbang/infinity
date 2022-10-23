# 本地部署

PIP_MIRROR=http://127.0.0.1:7104/root/pypi/+simple/
PIP_MIRROR_HOST=127.0.0.1:7104

project=
index=1
docker build --network=host --build-arg PIP_MIRROR=${PIP_MIRROR} --build-arg PIP_MIRROR_HOST=${PIP_MIRROR_HOST} -f ./CerelyScheduleDockerfile -t dao-celery-schedule:latest .


docker run -d --privileged=true  -e "profiles={{env}}" --name=${project}-${index} -e "index=${index}" -e "route=${route}" -e "FLASK_ENV=${env}" -e "thread=${thread}" --net=host --rm -it "${project}":"${version}"
echo y | docker system prune