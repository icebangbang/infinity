# sh run-cerely.sh ~/Work/pem/ironmansre_cdh.pem deveploment dev 2 5 indicator
# sh run-cerely.sh ~/Work/pem/ironmansre_cdh.pem deveploment dev 1 1 default

pem=${1}
env=${2}
target=${3}
start=${4}
end=${5}
route=${6}
skipCopy=true


project=dao-celery
version=latest

docker build --no-cache -f ./CerelyDockerfile -t ${project}:${version} .
docker save ${project}:${version} > ${project}.tar


for ((index=${start}; index<=${end}; index++))
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
  -e skipCopy=${skipCopy} \
  -e route=${route}
done