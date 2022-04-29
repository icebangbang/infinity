# 进行远程化本地部署

# sh run-cerely.sh ~/Work/pem/xzhh.pem development test 6 15 indicator true
# sh run-cerely.sh ~/Work/pem/xzhh.pem development test 1 1 default true

# sh remote_local_build.sh ~/Work/pem/ironmansre_cdh.pem offline offline zz_lf Gitee158,




pem=${1}
env=${2}
target=${3}
gituser=${4}
gitpass=${5}



ansible-playbook \
  deploy/remote_site.yml \
  -i deploy/hosts \
  --private-key ${pem} \
  -e env=${env} \
  -e target=${target} \
  -e gituser=${gituser} \
  -e gitpass=${gitpass}