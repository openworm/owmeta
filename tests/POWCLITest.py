from __future__ import print_function
from collections import namedtuple
from rdflib.term import URIRef
import importlib as im
import io
from multiprocessing import Queue, Process
from os.path import join as p
import os
import re
import shlex
import shutil
from subprocess import check_output, CalledProcessError
import six
import sys
import tempfile
from textwrap import dedent
import traceback
import transaction
from pytest import mark, fixture
import unittest

from PyOpenWorm.data_trans.local_file_ds import LocalFileDataSource as LFDS
from PyOpenWorm import connect
from PyOpenWorm.datasource import DataTranslator
from PyOpenWorm.context import Context, IMPORTS_CONTEXT_KEY, DATA_CONTEXT_KEY
from PyOpenWorm.context_common import CONTEXT_IMPORTS


pytestmark = mark.pow_cli_test


@fixture
def self():
    res = Data()
    res.testdir = tempfile.mkdtemp(prefix=__name__ + '.')
    with open(p('tests', 'pytest-cov-embed.py'), 'r') as f:
        ptcov = f.read()
    # Added so pytest_cov gets to run for our subprocesses
    with open(p(res.testdir, 'sitecustomize.py'), 'w') as f:
        f.write(ptcov)
    shutil.copytree('.pow', p(res.testdir, '.pow'), symlinks=True)

    yield res

    shutil.rmtree(res.testdir)


class Data(object):
    exception = None

    def __str__(self):
        items = []
        for m in dir(self):
            if not (m.startswith('_') or m == 'sh'):
                items.append(m + '=' + str(getattr(self, m)))
        return 'Data({})'.format(', '.join(items))

    def sh(self, command, **kwargs):
        env = dict(os.environ)
        env['PYTHONPATH'] = self.testdir + os.pathsep + env['PYTHONPATH']
        try:
            return check_output(shlex.split(command), env=env, cwd=self.testdir, **kwargs).decode('utf-8')
        except CalledProcessError as e:
            if e.stdout:
                print(dedent('''\
                ----------stdout from "{}"----------
                {}
                ----------{}----------
                '''.format(command, e.stdout.decode('UTF-8'),
                           'end stdout'.center(14 + len(command)))))
            if e.stderr:
                print(dedent('''\
                ----------stderr from "{}"----------
                {}
                ----------{}----------
                '''.format(command, e.stderr.decode('UTF-8'),
                           'end stderr'.center(14 + len(command)))))
            raise

    __repr__ = __str__


def test_translator_list(self):
    ''' Test we have some translator '''
    assertRegexpMatches(self.sh('pow translator list'), r'<[^>]+>')


def test_source_list(self):
    ''' Test we have some data source '''
    assertRegexpMatches(self.sh('pow source list'), r'<[^>]+>')


def test_source_list_dweds(self):
    ''' Test listing of DWEDS '''
    out = self.sh('pow source list --kind :DataWithEvidenceDataSource')
    assertRegexpMatches(out, r'<[^>]+>')


def test_manual_graph_edit_no_diff(self):
    '''
    Edit a context file and do a diff -- there shouldn't be any difference because we ignore such manual updates
    '''
    index = self.sh('cat ' + p('.pow', 'graphs', 'index'))
    fname = index.split('\n')[0].split(' ')[0]

    open(p(self.testdir, '.pow', 'graphs', fname), 'w').close() # truncate a graph's serialization

    assertRegexpMatches(self.sh('pow diff'), r'^$')


def test_contexts_list(self):
    ''' Test we have some contexts '''
    assertRegexpMatches(self.sh('pow contexts list'), r'^http://')


def test_list_contexts(self):
    ''' Test we have some contexts '''
    assertRegexpMatches(self.sh('pow list_contexts'), r'^http://')


def test_save_diff(self):
    ''' Change something and make a diff '''
    modpath = p(self.testdir, 'test_module')
    os.mkdir(modpath)
    open(p(modpath, '__init__.py'), 'w').close()
    with open(p(modpath, 'command_test_save.py'), 'w') as out:
        print(dedent('''\
                from test_module.monkey import Monkey


                def pow_data(ns):
                    ns.context.add_import(Monkey.definition_context)
                    ns.context(Monkey)(bananas=55)
                '''), file=out)

    with open(p(modpath, 'monkey.py'), 'w') as out:
        print(dedent('''\
                from PyOpenWorm.dataObject import DataObject, DatatypeProperty


                class Monkey(DataObject):
                    class_context = 'http://example.org/primate/monkey'

                    bananas = DatatypeProperty()
                    def identifier_augment(self):
                        return type(self).rdf_namespace['paul']

                    def defined_augment(self):
                        return True


                __yarom_mapped_classes__ = (Monkey,)
                '''), file=out)
    print(self.sh('pow save test_module.command_test_save'))
    assertRegexpMatches(self.sh('pow diff'), r'<[^>]+>')


def test_save_classes(self):
    modpath = p(self.testdir, 'test_module')
    os.mkdir(modpath)
    open(p(modpath, '__init__.py'), 'w').close()
    with open(p(modpath, 'monkey.py'), 'w') as out:
        print(dedent('''\
                from PyOpenWorm.dataObject import DataObject, DatatypeProperty


                class Monkey(DataObject):
                    class_context = 'http://example.org/primate/monkey'

                    bananas = DatatypeProperty()
                    def identifier_augment(self):
                        return type(self).rdf_namespace['paul']

                    def defined_augment(self):
                        return True


                __yarom_mapped_classes__ = (Monkey,)
                '''), file=out)
    print(self.sh('pow save test_module.monkey'))
    assertRegexpMatches(self.sh('pow diff'), r'<[^>]+>')


def test_save_imports(self):
    modpath = p(self.testdir, 'test_module')
    os.mkdir(modpath)
    open(p(modpath, '__init__.py'), 'w').close()
    with open(p(modpath, 'monkey.py'), 'w') as out:
        print(dedent('''\
                from PyOpenWorm.dataObject import DataObject, DatatypeProperty

                class Monkey(DataObject):
                    class_context = 'http://example.org/primate/monkey'

                    bananas = DatatypeProperty()
                    def identifier_augment(self):
                        return type(self).rdf_namespace['paul']

                    def defined_augment(self):
                        return True


                class Giraffe(DataObject):
                    class_context = 'http://example.org/ungulate/giraffe'


                def pow_data(ns):
                    ns.context.add_import(Monkey.definition_context)
                    ns.context.add_import(Giraffe.definition_context)

                __yarom_mapped_classes__ = (Monkey,)
                '''), file=out)
    print(self.sh('pow save test_module.monkey'))
    with connect(p(self.testdir, '.pow', 'pow.conf')) as conn:
        ctx = Context(ident=conn.conf[IMPORTS_CONTEXT_KEY], conf=conn.conf)
        trips = set(ctx.stored.rdf_graph().triples((None, None, None)))
        assert (URIRef(conn.conf[DATA_CONTEXT_KEY]),
                CONTEXT_IMPORTS,
                URIRef('http://example.org/primate/monkey')) in trips
        assert (URIRef(conn.conf[DATA_CONTEXT_KEY]),
                CONTEXT_IMPORTS,
                URIRef('http://example.org/ungulate/giraffe')) in trips


class DT1(DataTranslator):
    class_context = 'http://example.org/context'
    translator_identifier = URIRef('http://example.org/trans1')

    def translate(source):
        pass


def test_translator_list(self):
    expected = URIRef('http://example.org/trans1')
    with connect(p(self.testdir, '.pow', 'pow.conf')) as conn:
        with transaction.manager:
            # Create data sources
            ctx = Context(ident='http://example.org/context', conf=conn.conf)
            ctx.mapper.process_class(DT1)

            DT1.definition_context.save(conn.conf['rdf.graph'])
            # Create a translator
            dt = ctx(DT1)()

            ctx_id = conn.conf['data_context_id']
            main_ctx = Context(ident=ctx_id, conf=conn.conf)
            main_ctx.add_import(ctx)
            main_ctx.save_imports()
            ctx.save()

    # List translators
    assertRegexpMatches(
        self.sh('pow translator list'),
        re.compile('^' + expected.n3() + '$', flags=re.MULTILINE)
    )


class DT2(DataTranslator):
    class_context = 'http://example.org/context'
    input_type = LFDS
    output_type = LFDS
    translator_identifier = 'http://example.org/trans1'

    def translate(source):
        print(source.full_path())
        return source


@mark.xfail
def test_translate_data_source_loader(self):
    with connect(p(self.testdir, '.pow', 'pow.conf')) as conn:
        with transaction.manager:
            # Create data sources
            ctx = Context(ident='http://example.org/context', conf=conn.conf)
            ctx(LFDS)(
                ident='http://example.org/lfds',
                file_name='Merged_Nuclei_Stained_Worm.zip',
                torrent_file_name='d9da5ce947c6f1c127dfcdc2ede63320.torrent'
            )
            ctx.mapper.process_class(DT2)
            dt = ctx(DT2)()
            # Create a translator
            ctx_id = conn.conf['data_context_id']
            DT2.definition_context.save(conn.conf['rdf.graph'])
            main_ctx = Context(ident=ctx_id, conf=conn.conf)
            main_ctx.add_import(ctx)
            main_ctx.save_imports()
            ctx.save()

    # Do translation
    assertRegexpMatches(
        self.sh('pow translate http://example.org/trans1 http://example.org/lfds'),
        r'Merged_Nuclei_Stained_Worm.zip'
    )


def assertRegexpMatches(text, pattern):
    if isinstance(pattern, six.string_types):
        pattern = re.compile(pattern)
    if not pattern.search(text):
        raise AssertionError('Could not find {} in:\n{}'.format(pattern, text))
