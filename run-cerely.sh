# sh run-cerely.sh ~/Work/pem/ironmansre_cdh.pem deveploment dev 2
# sh run-cerely.sh ~/Work/pem/jumper.pem deveploment jumper 2

pem=${1}
env=${2}
target=${3}
num=${4}
skipCopy=true


project=dao-celery
version=latest

docker build -f ./CerelyDockerfile -t ${project}:${version} .
docker save ${project}:${version} > ${project}.tar


for ((index=1; index<=num; index++))
do

echo ${index}
if (( ${index} == 1 ));then
  skipCopy=false
#  echo ${skipCopy}
else
  skipCopy=true
#  echo ${skipCopy}
fi

echo ${skipCopy}
ansible-playbook \
  deploy/celery/site.yml \
  -i deploy/celery/hosts \
  --private-key ${pem} \
  -e image=../${project}.tar \
  -e env=${env} \
  -e target=${target} \
  -e project=${project} \
  -e version=${version} \
  -e index=${index} \
  -e skipCopy=${skipCopy}
done