import tempfile
from pathlib import Path
from unittest.mock import patch

import bottle


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
