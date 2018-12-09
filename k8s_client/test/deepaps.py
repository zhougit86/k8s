from k8s_client.client import Client


client = Client(
    "v1",
    host="172.12.78.51",
    port=6443,
    key_file="/home/zhouning/vm/kubecfg-fl-key.pem",
    cert_file="/home/zhouning/vm/kubecfg-fl-client.pem",
)


def create_db_service():
    client.create_external_service("deepaps-db", 5432, "172.12.78.2", 5432)


def delete_db_service():
    print(client.service.delete("default", "deepaps-db"))


def do_create():
    containers = [
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

    port_map = {
        5080: {
            "name": "deepaps-port",
            "node_port": 30680,
            "cluster_port": 15080,
        },
        5081: {
            "name": "deepaps-weixin-port",
            "node_port": 30681,
            "cluster_port": 15081,
        },
    }

    client.create_deployment("deepaps-sys", containers, port_map)
    # client.create_deployment("deepaps-sys", containers)


def do_delete():
    print(client.deployment.delete("default", "deepaps-sys"))


# do_delete()
do_create()
