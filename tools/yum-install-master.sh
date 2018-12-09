#!/usr/bin/env bash

systemctl stop firewalld
systemctl disable firewalld
setenforce 0
sed -i '/^SELINUX=/c SELINUX=disabled' /etc/sysconfig/selinux

yum -y install etcd flannel kubernetes


sed -i '/^ETCD_LISTEN_CLIENT_URLS/c ETCD_LISTEN_CLIENT_URLS="http://0.0.0.0:2379"' /etc/etcd/etcd.conf
cp apiserver.cfg /etc/kubernetes/apiserver

for service in etcd kube-apiserver kube-controller-manager kube-scheduler
do
systemctl restart ${service}
systemctl enable ${service}
systemctl status ${service}
done

kubectl config set-cluster k8s-cluster1 --server=http://localhost:9090
kubectl config set-context kube-system-ctx --cluster=k8s-cluster1
kubectl config use-context kube-system-ctx
kubectl config view

etcdctl set /atomic.io/network/config '{"Network":"10.1.0.0/16"}'

for service in flanneld
do
systemctl restart ${service}
systemctl enable ${service}
systemctl status ${service}
done

sed -i '/^KUBE_CONTROLLER_MANAGER_ARGS/c KUBE_CONTROLLER_MANAGER_ARGS="--master=http://127.0.0.1:9090"' /etc/kubernetes/controller-manager
sed -i '/^KUBE_SCHEDULER_ARGS/c /KUBE_SCHEDULER_ARGS="--master=http://127.0.0.1:9090"' /etc/kubernetes/scheduler
