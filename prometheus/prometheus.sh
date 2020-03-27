kubectl delete service prometheus -n openfaas
sleep 30
kubectl create -f /home/ubuntu/prometheus/prometheus-service.yml