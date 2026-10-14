import tempfile
from io import BytesIO
from pathlib import Path
from unittest.mock import patch

import bottle
from .tools import ServerTestBase


def test_adapter():
    plugin = lambda fn: lambda: 'adapted-' + fn()
    adapter = bottle._adapt_plugin(plugin)

    assert isinstance(adapter, bottle._CallablePluginAdapter)
    assert adapter.apply(lambda: 'ok', None)() == 'adapted-ok'


def test_chain():
    handler = bottle._CAST_HANDLER_CHAIN

    for cls in (
        bottle._CastBytesHandler,
        bottle._CastHTTPErrorHandler,
        bottle._CastHTTPResponseHandler,
        bottle._CastFileHandler,
        bottle._CastIterableHandler,
    ):
        assert isinstance(handler, cls)
        handler = handler._next_handler

    assert handler is None

    with patch.object(
        bottle._CastBytesHandler,
        '__init__',
        side_effect=AssertionError('Handler recreated')
    ):
        assert list(bottle.Bottle()._cast(b'ok')) == [b'ok']


def test_strategy():
    for name, cls in (
        ('FULL', bottle._StaticFileFullStrategy),
        ('HEAD', bottle._StaticFileHeadStrategy),
        ('RANGE', bottle._StaticFileRangeStrategy),
    ):
        strategy = getattr(
            bottle, '_STATIC_FILE_' + name + '_STRATEGY'
        )
        assert isinstance(strategy, cls)

    with tempfile.TemporaryDirectory() as root:
        Path(root, 'file.txt').write_bytes(b'data')

        with patch.object(
            bottle._StaticFileFullStrategy,
            '__init__',
            side_effect=AssertionError('Strategy recreated')
        ):
            response = bottle.static_file('file.txt', root=root)
            try:
                assert response.body.read() == b'data'
            finally:
                response.body.close()


def test_template_method():
    for cls in (
        bottle.SimpleTemplate,
        bottle.MakoTemplate,
        bottle.Jinja2Template,
        bottle.CheetahTemplate,
    ):
        assert cls.render is bottle.BaseTemplate.render

    template = bottle.SimpleTemplate('{{value}}')
    template.defaults = {'value': 'default'}

    assert template.render() == 'default'
    assert template.render(value='updated') == 'updated'


def test_adapter_identity():
    class Plugin:
        def apply(self, callback, route):
            return callback

    plugin = Plugin()
    assert bottle._adapt_plugin(plugin) is plugin


def test_chain_delegation():
    class Last(bottle._CastHandler):
        def handle(self, app, out):
            return [out]

    handler = bottle._CastHandler(Last())
    assert handler.handle(None, b'data') == [b'data']


def test_template_context():
    class Template(bottle.BaseTemplate):
        def prepare(self, **options):
            pass

        def _render(self, context):
            return context.copy()

    template = Template('text')
    template.defaults = {'name': 'default', 'fixed': 'yes'}

    values = {'name': 'override'}

    assert template.render(values) == {
        'name': 'override',
        'fixed': 'yes'
    }
    assert template.render(name='other')['name'] == 'other'
    assert template.defaults['name'] == 'default'
    assert values == {'name': 'override'}


class TestPatternEdges(ServerTestBase):
    def test_chain_responses(self):
        self.app.get('/empty', callback=lambda: '')
        self.app.get(
            '/response',
            callback=lambda: bottle.HTTPResponse('created', status=201)
        )
        self.app.get(
            '/error',
            callback=lambda: bottle.HTTPError(404, 'missing')
        )
        self.app.error(404)(lambda error: 'not found')

        self.assertBody('', '/empty')
        self.assertStatus(201, '/response')
        self.assertBody('created', '/response')
        self.assertStatus(404, '/error')
        self.assertBody('not found', '/error')

    def test_chain_iterables(self):
        self.app.get('/file', callback=lambda: BytesIO(b'file data'))
        self.app.get(
            '/chunks',
            callback=lambda: iter(['first', 'second'])
        )

        self.assertBody('file data', '/file')
        self.assertBody('firstsecond', '/chunks')

    def test_static_file_methods(self):
        with tempfile.TemporaryDirectory() as root:
            Path(root, 'file.txt').write_bytes(b'abcdef')

            self.app.get(
                '/file',
                callback=lambda: bottle.static_file(
                    'file.txt', root=root
                )
            )

            self.assertBody('abcdef', '/file')

            head = self.urlopen('/file', method='HEAD')
            assert head['code'] == 200
            assert head['body'] == b''
            assert head['header']['Content-Length'] == '6'

            partial = self.urlopen(
                '/file',
                env={'HTTP_RANGE': 'bytes=1-3'}
            )
            assert partial['code'] == 206
            assert partial['body'] == b'bcd'
            assert partial['header']['Content-Range'] == 'bytes 1-3/6'

            invalid = self.urlopen(
                '/file',
                env={'HTTP_RANGE': 'bytes=99-100'}
            )
            assert invalid['code'] == 416
