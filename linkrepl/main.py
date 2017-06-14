from functools import partial

import tornado.curl_httpclient
import tornado.ioloop
import tornado.web

from linkrepl import yamlcache

__HTTP_CLIENT = None


def _get_http_client():
    global __HTTP_CLIENT
    if __HTTP_CLIENT is None:
        __HTTP_CLIENT = tornado.curl_httpclient.CurlAsyncHTTPClient()
    return __HTTP_CLIENT


class LinkHandler(tornado.web.RequestHandler):
    def initialize(self):
        self.http_client = _get_http_client()

    def _on_yaml_cache(self, tags, cache: yamlcache.CachedYaml):
        if not cache:
            return self.send_error(400, reason='Failed to load yaml to cache')
        link = cache.generate_link(tags)
        if not link:
            return self.send_error(404, reason='Failed to generate link for tags {}'.format(tags))
        return self.redirect(link)

    @tornado.web.asynchronous
    def get(self):
        link = self.get_argument('src')
        tags = self.get_arguments('t')
        yamlcache.get_cached_yaml(
            link,
            self.http_client,
            partial(self._on_yaml_cache, tags)
        )


def make_app():
    return tornado.web.Application(
        [
            (r'/ln', LinkHandler)
        ],
        debug=True)


if __name__ == '__main__':
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
