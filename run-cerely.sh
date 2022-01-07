# sh run-cerely.sh ~/Work/pem/xzhh.pem deveploment test 6 15 indicator true
# sh run-cerely.sh ~/Work/pem/xzhh.pem deveploment test 1 1 default true

# sh run-cerely.sh ~/Work/pem/xzhh.pem deveploment test 2 5 day_level false



pem=${1}
env=${2}
target=${3}
start=${4}
end=${5}
route=${6}
skipCopy=${7}


project=dao-celery
version=latest

echo ${skipCopy}
if [ "${skipCopy}" = false ];then
docker build --no-cache -f ./CerelyDockerfile -t ${project}:${version} .
docker save ${project}:${version} > ${project}.tar
fi

first_loop=0
for ((index=${start}; index<=${end}; index++))
do

echo ${index}

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

first_loop=0
done