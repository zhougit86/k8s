from k8s_client.v1.base import Base


class Node(Base):
    def __init__(self, rest, api_version):
        super(Node, self).__init__(rest, "nodes", api_version=api_version)
