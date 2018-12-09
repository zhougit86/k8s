from k8s_client.v1.base import Base


class Pod(Base):
    def __init__(self, rest, api_version):
        super(Pod, self).__init__(rest, "pods", api_version=api_version)
