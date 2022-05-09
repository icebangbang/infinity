# 进行远程化本地部署

# sh run-cerely.sh ~/Work/pem/xzhh.pem development test 6 15 indicator true
# sh run-cerely.sh ~/Work/pem/xzhh.pem development test 1 1 default true

# sh remote_local_build.sh ~/Work/pem/ironmansre_cdh.pem offline offline /home/ironmansre/infinity [6,7,8,9,10,11,12,13,14,15,16] zz_lf x

# sh remote_local_build.sh ~/Work/pem/xzhh.pem test test2 ~/infinity [6,7,8,9,10,11] zz_lf xxx
# sh remote_local_build.sh ~/Work/pem/xzhh.pem test test ~/infinity [6,7,8,9,10,11] zz_lf xxx




pem=${1}
env=${2}
target=${3}
dest=${4}
indicator_task_item=${5}
gituser=${6}
gitpass=${7}



/usr/local/bin/ansible-playbook \
  deploy/remote_site.yml \
  -i deploy/hosts \
  --private-key ${pem} \
  -e env=${env} \
  -e target=${target} \
  -e dest=${dest} \
  -e gituser=${gituser} \
  -e gitpass=${gitpass} \
  -e ind_item=${indicator_task_item}