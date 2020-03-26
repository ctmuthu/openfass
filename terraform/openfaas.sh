curl -sL https://cli.openfaas.com | sudo sh
git clone https://github.com/openfaas/faas-netes
kubectl apply -f https://raw.githubusercontent.com/openfaas/faas-netes/master/namespaces.yml

PASSWORD=$(head -c 12 /dev/urandom | shasum| cut -d' ' -f1)

echo $PASSWORD > password.txt

echo $PASSWORD

kubectl -n openfaas create secret generic basic-auth \
--from-literal=basic-auth-user=admin \
--from-literal=basic-auth-password="$PASSWORD"

cd faas-netes && \
kubectl apply -f ./yaml

sleep 60

kubectl port-forward svc/gateway -n openfaas 31112:8080 &

sleep 10

cd ..

export OPENFAAS_URL=http://127.0.0.1:31112

echo -n $(cat password.txt) | faas-cli login --password-stdin

faas-cli store deploy figlet

