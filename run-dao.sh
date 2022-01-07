# sh run-dao.sh ~/Work/pem/xzhh.pem test test true


pem=${1}
env=${2}
target=${3}
skipCopy=${4}


project=dao
version=latest


docker build -f ./Dockerfile -t ${project}:${version} .
docker save ${project}:${version} > ${project}.tar


ansible-playbook \
  deploy/dao/site.yml \
  -i deploy/dao/hosts \
  --private-key ${pem} \
  -e image=../${project}.tar \
  -e env=${env} \
  -e target=${target} \
  -e project=${project} \
  -e version=${version} \
  -e skipCopy=${skipCopy} \
  -e port=20500 \
  -e index=1
