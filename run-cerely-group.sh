echo 'y' | docker system prune
sh run-cerely-job.sh ~/Work/pem/xzhh.pem test test false
sh run-cerely.sh ~/Work/pem/xzhh.pem test test 1 1 default false
sh run-cerely.sh ~/Work/pem/xzhh.pem test test 2 2 day_level true
sh run-cerely.sh ~/Work/pem/xzhh.pem test test 6 11 indicator true