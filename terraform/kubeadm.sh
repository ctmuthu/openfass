sudo apt-get -y update

sudo apt-get install \
     apt-transport-https \
     ca-certificates \
     curl \
     gnupg-agent \
     software-properties-common -y

sleep 1

sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -

sleep 1

sudo apt-key fingerprint 0EBFCD88

echo "Muthu"

sleep 1

sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"

sleep 1

sudo apt-get update -y

echo "Muthu2"

#sudo apt-get install -y docker-ce=17.03.2~ce-0~ubuntu-xenial
  #containerd.io=1.2.10-3 \
  #docker-ce=5:19.03.4~3-0~ubuntu-$(lsb_release -cs) #\
 # docker-ce-cli=5:19.03.4~3-0~ubuntu-$(lsb_release -cs)

 apt-get install -y \
    containerd.io=1.2.10-3 \
    docker-ce=5:19.03.4~3-0~ubuntu-$(lsb_release -cs) \
    docker-ce-cli=5:19.03.4~3-0~ubuntu-$(lsb_release -cs)

sudo apt-get update -y && sudo apt-get install -y apt-transport-https curl
curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
cat <<EOF | sudo tee /etc/apt/sources.list.d/kubernetes.list
deb https://apt.kubernetes.io/ kubernetes-xenial main
EOF
sudo apt-get update -y
sleep 1
sudo apt-get install -y kubelet kubeadm kubectl
sudo apt-mark hold kubelet kubeadm kubectl