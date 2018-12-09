from k8s_client.v1.base import RestAPI
from k8s_client.v1.node import Node
from k8s_client.v1.pod import Pod
from k8s_client.v1.service import Service, Endpoints
from k8s_client.v1.deployment import Deployment


class ClientV1(RestAPI):
    def __init__(self, host, port, cert_file, key_file):
        super(ClientV1, self).__init__(host, port, cert_file, key_file)
        self.node = Node(self, "v1")
        self.pod = Pod(self, "v1")
        self.service = Service(self, "v1")
        self.endpoint = Endpoints(self, "v1")
        self.deployment = Deployment(self, "v1")

    def _print_response(self, resp):
        print resp['status'] if resp.get("kind") == "Status" else "OK", resp

    def create_external_service(self, name, port, target_host, target_port):
        """
        example, create external psql connection:
        client.create_external_service("deepaps-db", 5432, "172.12.78.2", 5432)
        :param name:
        :param port:
        :param target_host:
        :param target_port:
        :return:
        """
        body = {
            "metadata": {"name": name},
            "spec": {
                "ports": [{"port": port, "protocol": "TCP"}]
            }
        }
        resp = self.service.create("default", **body)
        self._print_response(resp)

        body = {
            "metadata": {"name": name},
            "subsets": [
                {
                    "addresses": [{"ip": target_host}],
                    "ports": [{"port": target_port}]
                }
            ]
        }
        resp = self.endpoint.create("default", **body)
        self._print_response(resp)

    def create_node_service(self, name, selector_label_name, port_map):
        port_map_list = [
            {
                "targetPort": k,
                "name": v.get('name') if v.get('name') else "%s-%s" % (name, k),
                "port": v['cluster_port'],
                "nodePort": v['node_port'],
                "protocol": "TCP"
            } for k, v in port_map.items()
        ]
        body = {
            "metadata": {"name": name},
            "spec": {
                "ports": port_map_list,
                "selector": {"name": selector_label_name},
                "type": "NodePort"
            }
        }
        resp = self.service.create("default", **body)
        self._print_response(resp)

    def create_deployment(self, name, containers, port_map=None):
        label_name = name + "-label"
        body = {
            "metadata": {"name": name},
            "spec": {
                "replicas": 1,
                "selector": {
                    "matchLabels": {"name": label_name}
                },
                "template": {
                    "metadata": {"labels": {"name": label_name}},
                    "spec": {"containers": containers}
                }
            }
        }
        resp = self.deployment.create("default", **body)
        self._print_response(resp)

        if port_map:
            self.create_node_service(name + "-svc", label_name, port_map)



