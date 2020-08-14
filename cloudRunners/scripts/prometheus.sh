wget https://github.com/prometheus/prometheus/releases/download/v2.20.1/prometheus-2.20.1.linux-amd64.tar.gz
tar xvf prometheus-2.20.1.linux-amd64.tar.gz
cd prometheus-2.20.1.linux-amd64/
groupadd --system prometheus
grep prometheus /etc/group
useradd -s /sbin/nologin -r -g prometheus prometheus
id prometheus
mkdir -p /etc/prometheus/{rules,rules.d,files_sd}  /var/lib/prometheus
cp prometheus promtool /usr/local/bin/
cp -r consoles/ console_libraries/ /etc/prometheus/
cp /home/ubuntu/scripts/prometheus.service /etc/systemd/system/prometheus.service
cp /home/ubuntu/scripts/prometheus.yml /etc/prometheus/prometheus.yml
chown -R prometheus:prometheus /etc/prometheus/  /var/lib/prometheus/
chmod -R 775 /etc/prometheus/ /var/lib/prometheus/
sleep 5
systemctl start prometheus
sleep 5
systemctl enable prometheus