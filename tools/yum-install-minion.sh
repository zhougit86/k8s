#!/usr/bin/env bash

if (( $# < 4 ))
then
    echo usage: "$0 <master_host_ip> <master_port> <local_docker_registry> <minion_host_ip>"
    exit -1
fi

master_host=$1
master_port=$2
local_docker_registry=$3
minion_host=$4


systemctl stop firewalld
systemctl disable firewalld
setenforce 0
sed -i '/^SELINUX=/c SELINUX=disabled' /etc/sysconfig/selinux

yum -y install flannel kubernetes docker


sed -i 's/--selinux-enabled/--selinux-enabled=false/' /etc/sysconfig/docker


sed -i '/^KUBE_MASTER/c KUBE_MASTER="--master=http://'${master_host}:${master_port}'"' /etc/kubernetes/config
echo 'KUBE_ETCD_SERVERS="--etcd_servers=http://'${master_host}':2379"' >> /etc/kubernetes/config


sed -i '/^KUBELET_ADDRESS/c KUBELET_ADDRESS="--address=0.0.0.0"' /etc/kubernetes/kubelet
sed -i 's/# KUBELET_PORT/KUBELET_PORT/' /etc/kubernetes/kubelet
sed -i '/^KUBELET_HOSTNAME/c KUBELET_HOSTNAME="--hostname-override='${minion_host}'"' /etc/kubernetes/kubelet
sed -i '/^KUBELET_API_SERVER/c KUBELET_API_SERVER="--api-servers=http://'${master_host}:${master_port}'"' /etc/kubernetes/kubelet


sed -i '/^FLANNEL_ETCD_ENDPOINTS/c FLANNEL_ETCD_ENDPOINTS="http://'${master_host}':2379"' /etc/sysconfig/flanneld


echo '{ "insecure-registries":["'${local_docker_registry}'"] }' > /etc/docker/daemon.json

for service in flanneld kube-proxy kubelet docker
do
systemctl restart ${service}
systemctl enable ${service}
systemctl status ${service}
done


yum install *rhsm* -y
wget http://mirror.centos.org/centos/7/os/x86_64/Packages/python-rhsm-certificates-1.19.10-1.el7_4.x86_64.rpm
rpm2cpio python-rhsm-certificates-1.19.10-1.el7_4.x86_64.rpm | cpio -iv --to-stdout ./etc/rhsm/ca/redhat-uep.pem | tee /etc/rhsm/ca/redhat-uep.pem
docker pull registry.access.redhat.com/rhel7/pod-infrastructure:latest




