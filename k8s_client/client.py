from k8s_client.v1.client import ClientV1


def Client(version="v1", **kwargs):
    if version == "v1":
        return ClientV1(
            kwargs.get("host", "localhost"),
            kwargs.get("port", 6443),
            kwargs.get("cert_file"),
            kwargs.get("key_file")
        )
