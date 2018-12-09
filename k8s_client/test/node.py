from k8s_client.client import Client


client = Client(
    "v1",
    host="172.12.78.51",
    port=6443,
    key_file="/home/zhouning/vm/kubecfg-fl-key.pem",
    cert_file="/home/zhouning/vm/kubecfg-fl-client.pem",
)
print(client.node.list("all")['items'][0]['metadata'])
