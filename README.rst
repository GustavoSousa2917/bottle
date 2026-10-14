.. image:: https://bottlepy.org/docs/dev/_static/logo_nav.png
  :target: https://bottlepy.org/
  :alt: Bottle Logo
  :align: right

.. image:: https://github.com/bottlepy/bottle/workflows/Tests/badge.svg
    :target: https://github.com/bottlepy/bottle/workflows/Tests
    :alt: Tests Status

.. image:: https://img.shields.io/pypi/v/bottle.svg
    :target: https://pypi.python.org/pypi/bottle/
    :alt: Latest Version

.. image:: https://img.shields.io/pypi/l/bottle.svg
    :target: https://pypi.python.org/pypi/bottle/
    :alt: License

.. _Python: https://python.org/
.. _mako: https://www.makotemplates.org/
.. _cheetah: https://www.cheetahtemplate.org/
.. _jinja2: https://jinja.palletsprojects.com/

.. _WSGI: https://peps.python.org/pep-3333/
.. _gunicorn: https://gunicorn.org/
.. _paste: https://pythonpaste.readthedocs.io/
.. _cheroot: https://cheroot.cherrypy.dev/

============================
Bottle: Python Web Framework
============================

Bottle is a fast, simple and lightweight WSGI_ micro web-framework for Python_. It is distributed as a single file module and has no dependencies other than the `Python Standard Library <https://docs.python.org/library/>`_.

* **Routing:** Requests to function-call mapping with support for clean and dynamic URLs.
* **Templates:** Fast `built-in template engine <https://bottlepy.org/docs/dev/tutorial.html#tutorial-templates>`_ and support for mako_, jinja2_ and cheetah_ templates.
* **Utilities:** Convenient access to form data, file uploads, cookies, headers and other HTTP features.
* **Server:** Built-in development server and ready-to-use adapters for a wide range of WSGI_ capable HTTP server (e.g. gunicorn_, paste_ or cheroot_).


Homepage and documentation: https://bottlepy.org


Example: "Hello World" in a bottle
----------------------------------

.. code-block:: python

  from bottle import route, run, template

  @route('/hello/<name>')
  def index(name):
      return template('<b>Hello {{name}}</b>!', name=name)

  run(host='localhost', port=8080)

Run this script or paste it into a Python console, then point your browser to `<http://localhost:8080/hello/world>`_. That's it.


Download and Install
--------------------

.. __: https://github.com/bottlepy/bottle/raw/main/bottle.py

Install the latest stable release with ``pip install bottle`` or download `bottle.py`__ (unstable) into your project directory. There are no hard dependencies other than the Python standard library.


Padrões de Projeto
------------------

Esta branch implementa quatro padrões de projeto no arquivo
``bottle.py``, visando melhorar a organização, reutilização
e manutenção do código.

Adapter
~~~~~~~

A classe ``_CallablePluginAdapter`` adapta plugins baseados
em funções para a interface ``apply()``.

Isso permite que diferentes tipos de plugins sejam utilizados
de maneira uniforme pelo sistema de rotas.

Chain of Responsibility
~~~~~~~~~~~~~~~~~~~~~~~

A classe ``_CastHandler`` define uma cadeia de processamento
de respostas HTTP.

Cada handler verifica se consegue processar a resposta.
Caso contrário, delega a responsabilidade ao próximo handler.

A cadeia reutiliza as instâncias dos handlers, evitando
criações desnecessárias de objetos.

Strategy
~~~~~~~~

O processamento de arquivos estáticos utiliza três estratégias:

* ``_StaticFileFullStrategy``: respostas completas.
* ``_StaticFileHeadStrategy``: requisições HEAD.
* ``_StaticFileRangeStrategy``: respostas parciais.

Cada estratégia encapsula um comportamento específico,
permitindo separar as responsabilidades.

Template Method
~~~~~~~~~~~~~~~

O método ``BaseTemplate.render()`` define o fluxo comum
de renderização de templates.

O método ``_render()`` permite que cada mecanismo implemente
seu comportamento específico.

O padrão é utilizado nas classes ``SimpleTemplate``,
``MakoTemplate``, ``Jinja2Template`` e ``CheetahTemplate``.

Testes
~~~~~~

Os testes específicos estão localizados em
``test/test_design_patterns.py``.

Para executar todos os testes:

.. code-block:: console

   python3 -m pytest -q

License
-------

.. __: https://github.com/bottlepy/bottle/raw/main/LICENSE

Code and documentation are available according to the MIT License (see LICENSE__).

The Bottle logo however is *NOT* covered by that license. It is allowed to use the logo as a link to the bottle homepage or in direct context with the unmodified library. In all other cases, please ask first.
