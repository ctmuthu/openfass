curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3
chmod 700 get_helm.sh
./get_helm.sh
#helm repo add stable https://kubernetes-charts.storage.googleapis.com
sleep 10
sudo kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.0.3/aio/deploy/recommended.yaml
sleep 20
sudo cat <<EOF | sudo kubectl apply -f -
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: admin-user
  namespace: kubernetes-dashboard
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: admin-user
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: cluster-admin
subjects:
- kind: ServiceAccount
  name: admin-user
  namespace: kubernetes-dashboard
---
EOF

sleep 10
sudo kubectl -n kubernetes-dashboard describe secret $(sudo kubectl -n kubernetes-dashboard get secret | grep admin-user | awk '{print $1}')
sleep 10
sudo kubectl proxy &

sleep 10

curl -sL https://cli.openfaas.com | sudo sh

PASSWORD=$(head -c 12 /dev/urandom | shasum| cut -d' ' -f1)
echo $PASSWORD > password.txt
echo $PASSWORD

sudo kubectl apply -f scripts/01-namespaces.yaml
sleep 10
udo kubectl apply -k cadvisor/
sudo kubectl -n openfaas create secret generic basic-auth --from-literal=basic-auth-user=admin --from-literal=basic-auth-password="$PASSWORD"

sudo kubectl apply -f faas-netes/
sleep 20
sudo kubectl port-forward svc/gateway -n openfaas 31112:8080 &
sleep 10
export OPENFAAS_URL=http://127.0.0.1:31112
echo -n $(cat password.txt) | faas-cli login --password-stdin
faas-cli store deploy sentimentanalysis


# http://localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/