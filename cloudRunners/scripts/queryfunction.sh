sudo docker login -u ctmuthu93 -p rucJyk-jucfu3-corred
cd queryfunction/
ipaddress=$(dig +short myip.opendns.com @resolver1.opendns.com)
sed -i "s/ipaddress/$ipaddress/g" queryfunction/handler.py
faas-cli template pull
sudo faas build
sudo faas push