kubectl delete service prometheus -n openfaas
sleep 30
kubectl create -f /home/ubuntu/prometheus/prometheus-service.yml
kubectl create -f /home/ubuntu/prometheus/node-exporter.yml
kubectl create -f /home/ubuntu/prometheus/node-exporter-service.yml