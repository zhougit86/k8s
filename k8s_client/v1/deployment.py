from k8s_client.v1.base import Base


class Deployment(Base):
    def __init__(self, rest, api_version):
        super(Deployment, self).__init__(rest, "deployments", url_prefix="apis/apps", api_version=api_version)



body = {
    "apiVersion": "extensions/v1beta1",
    "kind": "Deployment",
    "metadata": {
        "name": "deepaps-sys",
        "namespace": "default"
    },
    "spec": {
        "replicas": 1,
        "selector": {
            "matchLabels": {
                "name": "deepaps-label"
            }
        },
        "template": {
            "metadata": {
                "labels": {
                    "name": "deepaps-label"
                }
            },
            "spec": {
                "containers": [
                    {
                        "command": [
                            "python3",
                            "usms.py"
                        ],
                        "image": "172.12.78.69:5000/img-usms:0.1",
                        "imagePullPolicy": "Always",
                        "name": "usms",
                        "ports": [
                            {
                                "containerPort": 5055
                            }
                        ],
                        "workingDir": "/root/backend"
                    },
                    {
                        "command": [
                            "python3",
                            "deepaps.py",
                            "-x"
                        ],
                        "image": "172.12.78.69:5000/img-deepaps:0.2",
                        "imagePullPolicy": "Always",
                        "name": "deepaps-backend",
                        "ports": [
                            {
                                "containerPort": 5080
                            }
                        ],
                        "workingDir": "/root/backend"
                    },
                    {
                        "command": [
                            "python3",
                            "deepaps_weixin.py",
                            "-x"
                        ],
                        "image": "172.12.78.69:5000/img-deepaps:0.2",
                        "imagePullPolicy": "Always",
                        "name": "deepaps-weixin-backend",
                        "ports": [
                            {
                                "containerPort": 5081
                            }
                        ],
                        "workingDir": "/root/backend"
                    },
                    {
                        "command": [
                            "/usr/bin/redis-server",
                            "/etc/redis/redis.conf"
                        ],
                        "image": "172.12.78.69:5000/img-redis:0.2",
                        "name": "deepaps-redis",
                        "ports": [
                            {
                                "containerPort": 6379
                            }
                        ]
                    }
                ]
            }
        }
    }
}

{
    "apiVersion": "v1",
    "kind": "Service",
    "metadata": {
        "labels": {
            "name": "deepaps-sys-service-label"
        },
        "name": "deepaps-sys-service",
        "namespace": "default"
    },
    "spec": {
        "ports": [
            {
                "name": "deepaps-port",
                "nodePort": 30580,
                "port": 15080,
                "protocol": "TCP",
                "targetPort": 5080
            },
            {
                "name": "deepaps-weixin-port",
                "nodePort": 30581,
                "port": 15081,
                "protocol": "TCP",
                "targetPort": 5081
            }
        ],
        "selector": {
            "name": "deepaps-label"
        },
        "type": "NodePort"
    }
}
