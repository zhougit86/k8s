from k8s_client.common.http_req import HttpReq


class RestAPI(object):
    def __init__(self, host, port, cert_file, key_file):
        self.req = HttpReq(host, port, cert_file, key_file)

    def get(self, url_prefix, api_version, path, **kwargs):
        return self.req.get("/%s/%s/%s" % (url_prefix, api_version, path), **kwargs)

    def post(self, url_prefix, api_version, path, **kwargs):
        return self.req.post("/%s/%s/%s" % (url_prefix, api_version, path), **kwargs)

    def delete(self, url_prefix, api_version, path, **kwargs):
        return self.req.delete("/%s/%s/%s" % (url_prefix, api_version, path), **kwargs)


class Base(object):
    def __init__(self, rest, resource, url_prefix="api", api_version="v1"):
        self.rest = rest
        self.kind = self.__class__.__name__
        print self.kind
        self.resource = resource
        self.url_prefix = url_prefix
        self.api_version = api_version

    def list(self, namespace, **kwargs):
        return self.rest.get(
            self.url_prefix,
            self.api_version,
            self.resource if namespace == "all" else "namespaces/%s/%s" % (namespace, self.resource),
            **kwargs
        )

    def delete(self, namespace, item, **kwargs):
        return self.rest.delete(
            self.url_prefix,
            self.api_version,
            "namespaces/%s/%s/%s" % (namespace, self.resource, item),
            **kwargs
        )

    def create(self, namespace, **kwargs):
        api, _, sub = self.url_prefix.partition('/')
        kwargs['apiVersion'] = "%s/%s" % (sub, self.api_version) if sub else self.api_version
        kwargs['kind'] = self.kind
        kwargs['metadata']['namespace'] = namespace
        print "in create:", kwargs
        return self.rest.post(
            self.url_prefix,
            self.api_version,
            "namespaces/%s/%s" % (namespace, self.resource),
            **kwargs
        )
