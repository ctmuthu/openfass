sudo docker login -u ctmuthu93 -p rucJyk-jucfu3-corred
cd miniodbmysql/
ipaddress=$(dig +short myip.opendns.com @resolver1.opendns.com)
sed -i "s/ipaddress/$ipaddress/g" miniodbmysql/handler.py
faas-cli template pull
sudo faas build
sudo faas push