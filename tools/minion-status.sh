#!/usr/bin/env bash

for service in flanneld kube-proxy kubelet docker
do
systemctl status ${service}
done
