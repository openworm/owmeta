from io import StringIO
from owmeta.bundle import Remote, URLConfig, HTTPBundleLoader
from owmeta.commands.bundle import OWMBundle


def test_write_read_remote_1():
    out = StringIO()
    r0 = Remote('remote')
    r0.write(out)
    out.seek(0)
    r1 = Remote.read(out)
    assert r0 == r1


def test_write_read_remote_2():
    out = StringIO()
    r0 = Remote('remote')
    r0.accessor_configs.append(URLConfig('http://example.org/bundle_remote0'))
    r0.accessor_configs.append(URLConfig('http://example.org/bundle_remote1'))
    r0.write(out)
    out.seek(0)
    r1 = Remote.read(out)
    assert r0 == r1


def test_get_http_url_loaders():
    '''
    Find loaders for HTTP URLs
    '''
    out = StringIO()
    r0 = Remote('remote')
    r0.accessor_configs.append(URLConfig('http://example.org/bundle_remote0'))
    for l in r0.generate_loaders(loader_classes=(HTTPBundleLoader,)):
        if isinstance(l, HTTPBundleLoader):
            return

    raise AssertionError('No HTTPBundleLoader was created')
