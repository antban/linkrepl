import yaml
import yaml.composer
import yaml.constructor


class CachedYaml(object):
    def __init__(self, yaml_link: str, keyword_lines: dict):
        self.yaml_link = yaml_link
        # keyword lines are frosenset->object
        self.keyword_lines = keyword_lines

    def _get_line_idx(self, keywords) -> object:
        result = None
        for k in self.keyword_lines:
            if all([i in k for i in keywords]):
                if result is None or len(k) < len(result):
                    result = k
        return self.keyword_lines.get(result) if result is not None else None

    def generate_link(self, keywords) -> str:
        line_idx = self._get_line_idx(keywords)
        return '{}#L{}'.format(self.yaml_link, line_idx) if line_idx else None


def yaml_to_keywords(yaml_data) -> dict:
    loader = yaml.Loader(yaml_data)

    def _compose_node(parent, index):
        line = loader.line
        node = yaml.composer.Composer.compose_node(loader, parent, index)
        node.__line__ = line + 1
        return node

    def _construct_mapping(node, deep=False):
        mapping = yaml.constructor.Constructor.construct_mapping(loader, node, deep=deep)
        mapping['__line__'] = node.__line__
        return mapping

    loader.compose_node = _compose_node
    loader.construct_mapping = _construct_mapping

    data = loader.get_single_data()

    # Now one have dict with line numbers, it is time to select keywords.
    def _guess_line(v):
        if isinstance(v, dict):
            return v['__line__']
        if isinstance(v, list):
            return _guess_line(v[0]) if v else None
        return None

    def _replace_name(x: str):
        return x.lower()

    def _recursive_load(found_so_far, node, result=None):
        if result is None:
            result = {}
        if isinstance(node, dict):
            for k, v in node.items():
                line = _guess_line(v)
                if not line:
                    continue
                tmp = found_so_far + [_replace_name(k)]
                print('Load: {} to line {}'.format(tmp, line))
                result[frozenset(tmp)] = line
                result = _recursive_load(tmp, v, result)
        elif isinstance(node, list):
            for n in node:
                result = _recursive_load(found_so_far, n, result)
        return result

    return _recursive_load([], data)


def link_to_raw(link):
    # Replaces https://github.com/zalando/nakadi/blob/master/api/nakadi-event-bus-api.yaml
    # to       https://raw.githubusercontent.com/zalando/nakadi/master/api/nakadi-event-bus-api.yaml
    import re
    match = re.search('https://github.com/(?P<project>.*)/blob/(?P<file>.*)', link)
    if not match:
        return None
    return 'https://raw.githubusercontent.com/{}/{}'.format(match.group('project'), match.group('file'))


__CACHE = dict()


def get_cached_yaml(link_src: str, http_client, on_data):
    link = link_src.lower()
    if link in __CACHE:
        return on_data(__CACHE.get(link))

    link_raw = link_to_raw(link)
    if not link_raw:
        return on_data(None)

    def _on_data(r):
        cached = None
        if not r.error:
            cached = CachedYaml(link, yaml_to_keywords(r.body))
            __CACHE[link] = cached
        return on_data(cached)

    print('Fetching {}'.format(link_src))
    http_client.fetch(link_raw, _on_data)
