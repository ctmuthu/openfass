kubectl apply -f kubernetes-metric-server/
kubectl apply -f kube-state-metrics/
kubectl apply -k cadvisor/

kubectl apply -f metrics-server-exporter/

curl -sL https://cli.openfaas.com | sudo sh

PASSWORD=$(head -c 12 /dev/urandom | shasum| cut -d' ' -f1)

echo $PASSWORD > password.txt

echo $PASSWORD

kubectl -n openfaas create secret generic basic-auth \
--from-literal=basic-auth-user=admin \
--from-literal=basic-auth-password="$PASSWORD"

#sudo cp ../prometheus/prometheus-cfg.yml ../faas-netes/yaml/prometheus-cfg.yml

kubectl apply -f faas-netes/

sleep 60

kubectl port-forward svc/gateway -n openfaas 31112:8080 &

sleep 10

export OPENFAAS_URL=http://127.0.0.1:31112

echo -n $(cat password.txt) | faas-cli login --password-stdin

faas-cli store deploy figlet

