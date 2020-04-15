kubectl delete service prometheus -n openfaas
sleep 30
echo "Prometheus service creation"
kubectl create -f /home/ubuntu/prometheus/