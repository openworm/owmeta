from __future__ import print_function
from rdflib.term import URIRef
from os.path import join as p
import os
import re
import shlex
import shutil
from contextlib import contextmanager
from subprocess import check_output, CalledProcessError
import six
import tempfile
from textwrap import dedent
import transaction
from pytest import mark, fixture

from owmeta.data_trans.local_file_ds import LocalFileDataSource as LFDS
from owmeta.datasource import DataTranslator
from owmeta.command import OWM
from owmeta.context import Context, IMPORTS_CONTEXT_KEY, DEFAULT_CONTEXT_KEY
from owmeta.context_common import CONTEXT_IMPORTS

from .TestUtilities import assertRegexpMatches

pytestmark = mark.owm_cli_test


def module_fixture():
    res = Data()
    res.testdir = tempfile.mkdtemp(prefix=__name__ + '.')
    res.test_homedir = p(res.testdir, 'homedir')
    os.mkdir(res.test_homedir)
    with open(p('tests', 'pytest-cov-embed.py'), 'r') as f:
        ptcov = f.read()
    # Added so pytest_cov gets to run for our subprocesses
    with open(p(res.testdir, 'sitecustomize.py'), 'w') as f:
        f.write(ptcov)

    try:
        yield res
    finally:
        shutil.rmtree(res.testdir)


def _fixture():
    with contextmanager(module_fixture)() as data:
        # Make a bundle
        shutil.copytree('.owm', p(data.testdir, '.owm'), symlinks=True)
        yield data


self = fixture(_fixture)


class Data(object):
    exception = None

    def __str__(self):
        items = []
        for m in vars(self):
            if (m.startswith('_') or m == 'sh'):
                continue
            items.append(m + '=' + repr(getattr(self, m)))
        return 'Data({})'.format(', '.join(items))

    def writefile(self, name, contents):
        with open(p(self.testdir, name), 'w') as f:
            print(dedent(contents), file=f)
            f.flush()

    def sh(self, *command, **kwargs):
        if not command:
            return None
        env = dict(os.environ)
        env['PYTHONPATH'] = self.testdir + os.pathsep + env['PYTHONPATH']
        env['HOME'] = self.test_homedir
        env.update(kwargs.pop('env', {}))
        outputs = []
        for cmd in command:
            try:
                outputs.append(check_output(shlex.split(cmd), env=env, cwd=self.testdir, **kwargs).decode('utf-8'))
            except CalledProcessError as e:
                if e.output:
                    print(dedent('''\
                    ----------stdout from "{}"----------
                    {}
                    ----------{}----------
                    ''').format(cmd, e.output.decode('UTF-8'),
                               'end stdout'.center(14 + len(cmd))))
                if getattr(e, 'stderr', None):
                    print(dedent('''\
                    ----------stderr from "{}"----------
                    {}
                    ----------{}----------
                    ''').format(cmd, e.stderr.decode('UTF-8'),
                               'end stderr'.center(14 + len(cmd))))
                raise
        return outputs[0] if len(outputs) == 1 else outputs

    __repr__ = __str__


def test_translator_list(self):
    ''' Test we have some translator '''
    assertRegexpMatches(self.sh('owm translator list'), r'<[^>]+>')


def test_source_list(self):
    ''' Test we have some data source '''
    assertRegexpMatches(self.sh('owm source list'), r'<[^>]+>')


def test_source_list_dweds(self):
    ''' Test listing of DWEDS '''
    out = self.sh('owm source list --kind :DataWithEvidenceDataSource')
    assertRegexpMatches(out, r'<[^>]+>')


def test_manual_graph_edit_no_diff(self):
    '''
    Edit a context file and do a diff -- there shouldn't be any difference because we ignore such manual updates
    '''
    index = self.sh('cat ' + p('.owm', 'graphs', 'index'))
    fname = index.split('\n')[0].split(' ')[0]

    open(p(self.testdir, '.owm', 'graphs', fname), 'w').close() # truncate a graph's serialization

    assertRegexpMatches(self.sh('owm diff'), r'^$')


def test_contexts_list(self):
    ''' Test we have some contexts '''
    assertRegexpMatches(self.sh('owm contexts list'), r'^http://')


def test_list_contexts(self):
    ''' Test we have some contexts '''
    assertRegexpMatches(self.sh('owm list_contexts'), r'^http://')


def test_save_diff(self):
    ''' Change something and make a diff '''
    modpath = p(self.testdir, 'test_module')
    os.mkdir(modpath)
    open(p(modpath, '__init__.py'), 'w').close()
    self.writefile(p(modpath, 'command_test_save.py'), '''\
        from test_module.monkey import Monkey


        def owm_data(ns):
            ns.context.add_import(Monkey.definition_context)
            ns.context(Monkey)(bananas=55)
        ''')

    self.writefile(p(modpath, 'monkey.py'), '''\
        from owmeta.dataObject import DataObject, DatatypeProperty


        class Monkey(DataObject):
            class_context = 'http://example.org/primate/monkey'

            bananas = DatatypeProperty()
            def identifier_augment(self):
                return type(self).rdf_namespace['paul']

            def defined_augment(self):
                return True


        __yarom_mapped_classes__ = (Monkey,)
        ''')
    print(self.sh('owm save test_module.command_test_save'))
    assertRegexpMatches(self.sh('owm diff'), r'<[^>]+>')


def test_save_classes(self):
    modpath = p(self.testdir, 'test_module')
    os.mkdir(modpath)
    open(p(modpath, '__init__.py'), 'w').close()
    self.writefile(p(modpath, 'monkey.py'), '''\
        from owmeta.dataObject import DataObject, DatatypeProperty


        class Monkey(DataObject):
            class_context = 'http://example.org/primate/monkey'

            bananas = DatatypeProperty()
            def identifier_augment(self):
                return type(self).rdf_namespace['paul']

            def defined_augment(self):
                return True


        __yarom_mapped_classes__ = (Monkey,)
        ''')
    print(self.sh('owm save test_module.monkey'))
    assertRegexpMatches(self.sh('owm diff'), r'<[^>]+>')


def test_save_imports(self):
    modpath = p(self.testdir, 'test_module')
    os.mkdir(modpath)
    open(p(modpath, '__init__.py'), 'w').close()
    self.writefile(p(modpath, 'monkey.py'), '''\
        from owmeta.dataObject import DataObject, DatatypeProperty

        class Monkey(DataObject):
            class_context = 'http://example.org/primate/monkey'

            bananas = DatatypeProperty()
            def identifier_augment(self):
                return type(self).rdf_namespace['paul']

            def defined_augment(self):
                return True


        class Giraffe(DataObject):
            class_context = 'http://example.org/ungulate/giraffe'


        def owm_data(ns):
            ns.context.add_import(Monkey.definition_context)
            ns.context.add_import(Giraffe.definition_context)

        __yarom_mapped_classes__ = (Monkey,)
        ''')
    print(self.sh('owm save test_module.monkey'))
    with OWM(owmdir=p(self.testdir, '.owm')).connect() as conn:
        ctx = Context(ident=conn.conf[IMPORTS_CONTEXT_KEY], conf=conn.conf)
        trips = set(ctx.stored.rdf_graph().triples((None, None, None)))
        assert (URIRef(conn.conf[DEFAULT_CONTEXT_KEY]),
                CONTEXT_IMPORTS,
                URIRef('http://example.org/primate/monkey')) in trips
        assert (URIRef(conn.conf[DEFAULT_CONTEXT_KEY]),
                CONTEXT_IMPORTS,
                URIRef('http://example.org/ungulate/giraffe')) in trips


class DT1(DataTranslator):
    class_context = 'http://example.org/context'
    translator_identifier = URIRef('http://example.org/trans1')

    def translate(source):
        pass


def test_translator_list(self):
    expected = URIRef('http://example.org/trans1')
    with OWM(owmdir=p(self.testdir, '.owm')).connect() as conn:
        with transaction.manager:
            # Create data sources
            ctx = Context(ident='http://example.org/context', conf=conn.conf)
            ctx.mapper.process_class(DT1)

            DT1.definition_context.save(conn.conf['rdf.graph'])
            # Create a translator
            dt = ctx(DT1)()

            ctx_id = conn.conf[DEFAULT_CONTEXT_KEY]
            main_ctx = Context(ident=ctx_id, conf=conn.conf)
            main_ctx.add_import(ctx)
            main_ctx.save_imports()
            ctx.save()

    # List translators
    assertRegexpMatches(
        self.sh('owm -o table translator list'),
        re.compile(expected.n3(), flags=re.MULTILINE)
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
    with OWM(owmdir=p(self.testdir, '.owm')).connect() as conn:
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
            ctx_id = conn.conf[DEFAULT_CONTEXT_KEY]
            DT2.definition_context.save(conn.conf['rdf.graph'])
            main_ctx = Context(ident=ctx_id, conf=conn.conf)
            main_ctx.add_import(ctx)
            main_ctx.save_imports()
            ctx.save()

    # Do translation
    assertRegexpMatches(
        self.sh('owm translate http://example.org/trans1 http://example.org/lfds'),
        r'Merged_Nuclei_Stained_Worm.zip'
    )
