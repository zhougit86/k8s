from k8s_client.v1.base import Base


class Service(Base):
    def __init__(self, rest, api_version):
        super(Service, self).__init__(rest, "services", api_version=api_version)


class Endpoints(Base):
    def __init__(self, rest, api_version):
        super(Endpoints, self).__init__(rest, "endpoints", api_version=api_version)

