

# sh run-cerely-job.sh ~/Work/pem/xzhh.pem test test false



pem=${1}
env=${2}
target=${3}

skipCopy=${4}


project=dao-celery-schedule
version=latest

if [ "${skipCopy}" = false ];then
docker build  -f ./CerelyScheduleDockerfile -t ${project}:${version} .
docker save ${project}:${version} > ${project}.tar
fi



ansible-playbook \
  deploy/celery_schedule/site.yml \
  -i deploy/celery_schedule/hosts \
  --private-key ${pem} \
  -e image=../${project}.tar \
  -e env=${env} \
  -e target=${target} \
  -e project=${project} \
  -e version=${version} \
  -e index=1 \
  -e skipCopy=${skipCopy} \

