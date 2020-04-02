variable "image" { type = string }
variable "region" { type = string }
variable "master_nodes" { type = list }
variable "worker_nodes" { type = list }
variable "master_nodes_private_ip" { type = list }
variable "worker_nodes_private_ip" { type = list }

provider "aws" {
  profile = "default"
  region  = var.region
}

resource "aws_default_vpc" "default" {
  tags = {
    Name = "Default VPC"
  }
}

resource "aws_subnet" "private_subnet" {
    cidr_block = "172.31.89.0/24"
    vpc_id = "${aws_default_vpc.default.id}"
  tags = {
    Name = "Private Subnet for Kubernetes Cluster"
  }
}

resource "aws_key_pair" "key" {
  key_name   = "same_for_all"
  public_key = file("~/.ssh/id_rsa.pub")
}

resource "aws_instance" "Worker" {
  count         = length(var.worker_nodes) 
  ami           = var.image
  instance_type = "t2.medium"
  tags = {
    Name = var.worker_nodes[count.index]
  }
  key_name      = "same_for_all"
  associate_public_ip_address   = true
  subnet_id     = "${aws_subnet.private_subnet.id}"
}

resource "aws_instance" "Master" {
  count         = length(var.master_nodes) 
  ami           = var.image
  instance_type = "t2.medium"
  associate_public_ip_address = true
  key_name = "same_for_all"
  subnet_id     = "${aws_subnet.private_subnet.id}"
  #private_ip = var.master_nodes_private_ip[count.index]
  provisioner "local-exec" {
    command = "cd .. && tar -zcvf scripts.tar.gz scripts"
  }
  provisioner "local-exec" {
    command = "cd .. && tar -zcvf grafana.tar.gz grafana"
  }
  provisioner "local-exec" {
    command = "cd .. && tar -zcvf prometheus.tar.gz prometheus"
  }
  provisioner "file" {
    source      = "~/.ssh/id_rsa"
    destination = "/home/ubuntu/id_rsa"
  }
  provisioner "file" {
    source      = "../scripts.tar.gz"
    destination = "/home/ubuntu/scripts.tar.gz"
  }
  provisioner "file" {
    source      = "../prometheus.tar.gz"
    destination = "/home/ubuntu/prometheus.tar.gz"
  }
  provisioner "file" {
    source      = "../grafana.tar.gz"
    destination = "/home/ubuntu/grafana.tar.gz"
  }
  connection {
    type        = "ssh"
    user        = "ubuntu"
    private_key = file("~/.ssh/id_rsa")
    host        = aws_instance.Master[count.index].public_ip
  }
  provisioner "remote-exec" {
    inline = [
      "sudo apt-get -y update",
      "sudo bash -c 'echo 1 > /proc/sys/net/ipv4/ip_forward'",
      "cd /home/ubuntu",
      "tar -zxvf scripts.tar.gz",
      "tar -zxvf grafana.tar.gz",
      "tar -zxvf prometheus.tar.gz",
      "sudo chmod 600 id_rsa",
      "sudo sh ./scripts/kubeadm.sh",
      "scp -oStrictHostKeyChecking=no -i id_rsa ./scripts/kubeadm.sh ubuntu@${aws_instance.Worker[0].private_ip}:/home/ubuntu/kubeadm.sh",
      "scp -oStrictHostKeyChecking=no -i id_rsa ./scripts/kubeadm.sh ubuntu@${aws_instance.Worker[1].private_ip}:/home/ubuntu/kubeadm.sh",
      "ssh -oStrictHostKeyChecking=no -i id_rsa ubuntu@${aws_instance.Worker[0].private_ip} 'sudo sh kubeadm.sh; '",
      "ssh -oStrictHostKeyChecking=no -i id_rsa ubuntu@${aws_instance.Worker[1].private_ip} 'sudo sh kubeadm.sh; '",
      "sudo kubeadm init",
      "mkdir -p $HOME/.kube",
      "sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config",
      "sudo chown $(id -u):$(id -g) $HOME/.kube/config",
      "sudo sh ./scripts/weave.sh",
      "sudo kubeadm token create --print-join-command | grep 'kubeadm join' | grep 'kubeadm join' > join.sh",
      "scp -oStrictHostKeyChecking=no -i id_rsa join.sh ubuntu@${aws_instance.Worker[0].private_ip}:/home/ubuntu/join.sh",
      "scp -oStrictHostKeyChecking=no -i id_rsa join.sh ubuntu@${aws_instance.Worker[1].private_ip}:/home/ubuntu/join.sh",
      "ssh -oStrictHostKeyChecking=no -i id_rsa ubuntu@${aws_instance.Worker[0].private_ip} 'sudo sh join.sh; '",
      "ssh -oStrictHostKeyChecking=no -i id_rsa ubuntu@${aws_instance.Worker[1].private_ip} 'sudo sh join.sh; '",
      "sudo sh ./scripts/openfaas.sh",
      "sudo sh ./prometheus/prometheus.sh",
      "sudo sh ./grafana/grafana.sh"
      ]
  }
  tags = {
    Name = var.master_nodes[count.index]
  }
}

output "master_ip" {
  value = aws_instance.Master[0].public_ip
}
