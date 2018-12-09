import httplib2
import json
import uuid


class HttpReq(object):
    def __init__(self, host, port, cert_file, key_file, session=None, header_get=None, header_post=None):
        self.h = httplib2.HTTPSConnectionWithTimeout(
            host,
            port,
            key_file=key_file,
            cert_file=cert_file,
            disable_ssl_certificate_validation=True
        )
        self.header_get = header_get if header_get else {
            'Connection': 'close',
        }
        self.header_post = header_post if header_post else {
            'Content-Type': 'application/json',
            'Connection': 'close',
        }
        if session == "uuid":
            session = uuid.uuid4().hex
        if session:
            self.header_get['Cookie'] = 'session = %s' % session
            self.header_post['Cookie'] = 'session = %s' % session

    def _debug(self, *args, **kwargs):
        print("HttpReq::", args, kwargs)

    def _json_format(self, resp, content):
        try:
            content = json.loads(content)
        except Exception as e:
            content = {'err': str(e), 'resp': resp, 'content': content}
            self._debug(**content)
        return content

    def get(self, url, **kwargs):
        if kwargs:
            url += "?%s" % '&'.join(["%s=%s" % (k, v) for k, v in kwargs.items()])
        self._debug("GET", url)
        self.h.request(
            "GET",
            url,
            # headers=self.header_get
        )
        resp = self.h.getresponse()
        return self._json_format(resp, resp.read())

    def post(self, url, **kwargs):
        self._debug("POST", url, **kwargs)
        self.h.request(
            'POST',
            url,
            json.dumps(kwargs).encode(),
            # headers=self.header_post
        )
        resp = self.h.getresponse()
        return self._json_format(resp, resp.read())

    def delete(self, url, **kwargs):
        self._debug("DELETE", url, **kwargs)
        self.h.request(
            'DELETE',
            url,
            json.dumps(kwargs).encode(),
            # headers=self.header_post
        )
        resp = self.h.getresponse()
        return self._json_format(resp, resp.read())
