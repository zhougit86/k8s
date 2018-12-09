#!/usr/bin/env bash

for service in etcd kube-apiserver kube-controller-manager kube-scheduler
do
systemctl status ${service}
done