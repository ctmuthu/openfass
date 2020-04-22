cd terraform
terraform destroy -var-file=var.tfvars -auto-approve && sleep 20 && terraform apply -var-file=var.tfvars -auto-approve && terraform output -json | jq 'with_entries(.value |= .value)' > config.json
sleep 60
cd ../grafana
terraform destroy --auto-approve && terraform apply --auto-approve
sleep 60
cd ../k6
k6 run --out influxdb=http://138.246.234.122:8086/myk6db script.js
sleep 20
k6 run --out influxdb=http://138.246.234.122:8086/myk6db script1.js
sleep 20
k6 run --out influxdb=http://138.246.234.122:8086/myk6db script2.js
sleep 20
k6 run --out influxdb=http://138.246.234.122:8086/myk6db script3.js
cat ../terraform/config.json
cd ..

#2

cd terraform
terraform destroy -var-file=var.tfvars -auto-approve && sleep 20 && terraform apply -var-file=t2large.tfvars -auto-approve && terraform output -json | jq 'with_entries(.value |= .value)' > config.json
sleep 60
cd ../grafana
terraform destroy --auto-approve && terraform apply --auto-approve
sleep 60
cd ../k6
k6 run --out influxdb=http://138.246.234.122:8086/myk6db script.js
sleep 20
k6 run --out influxdb=http://138.246.234.122:8086/myk6db script1.js
sleep 20
k6 run --out influxdb=http://138.246.234.122:8086/myk6db script2.js
sleep 20
k6 run --out influxdb=http://138.246.234.122:8086/myk6db script3.js
cat ../terraform/config.json
cd ..

#3

cd terraform
terraform destroy -var-file=t2large.tfvars -auto-approve && sleep 20 && terraform apply -var-file=t2xlarge.tfvars -auto-approve && terraform output -json | jq 'with_entries(.value |= .value)' > config.json
sleep 60
cd ../grafana
terraform destroy --auto-approve && terraform apply --auto-approve
sleep 60
cd ../k6
k6 run --out influxdb=http://138.246.234.122:8086/myk6db script.js
sleep 20
k6 run --out influxdb=http://138.246.234.122:8086/myk6db script1.js
sleep 20
k6 run --out influxdb=http://138.246.234.122:8086/myk6db script2.js
sleep 20
k6 run --out influxdb=http://138.246.234.122:8086/myk6db script3.js
cat ../terraform/config.json
sleep 60
cd ..

#4 

cd terraform
terraform destroy -var-file=t2xlarge.tfvars -auto-approve && sleep 20 && terraform apply -var-file=t22xlarge.tfvars -auto-approve && terraform output -json | jq 'with_entries(.value |= .value)' > config.json
sleep 60
cd ../grafana
terraform destroy --auto-approve && terraform apply --auto-approve
sleep 60
cd ../k6
k6 run --out influxdb=http://138.246.234.122:8086/myk6db script.js
sleep 20
k6 run --out influxdb=http://138.246.234.122:8086/myk6db script1.js
sleep 20
k6 run --out influxdb=http://138.246.234.122:8086/myk6db script2.js
sleep 20
k6 run --out influxdb=http://138.246.234.122:8086/myk6db script3.js
cat ../terraform/config.json
sleep 60
cd ..
