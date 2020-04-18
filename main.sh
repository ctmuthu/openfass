cd terraform
terraform destroy -var-file=var.tfvars -auto-approve && terraform apply -var-file=var.tfvars -auto-approve && terraform output -json | jq 'with_entries(.value |= .value)' > config.json
sleep 60
cd ../grafana
terraform destroy --auto-approve && terraform apply --auto-approve
sleep 60
cd ../k6
k6 run --out influxdb=http://138.246.234.122:8086/myk6db script.js
cat ../terraform/config.json