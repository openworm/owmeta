from __future__ import print_function
import unittest
try:
    from unittest.mock import MagicMock, Mock, ANY, patch
except ImportError:
    from mock import MagicMock, Mock, ANY, patch
import re
import tempfile
import os
from os import listdir, system as sh
from os.path import exists, join as p, realpath
from subprocess import check_output, CalledProcessError
import shlex
import shutil
import json
from rdflib.term import URIRef
from pytest import mark
import git
from PyOpenWorm.git_repo import GitRepoProvider, _CloneProgress
from PyOpenWorm.command import (POW, UnreadableGraphException, GenericUserError, StatementValidationError,
                                POWConfig, POWSource, POWTranslator, POWEvidence,
                                DATA_CONTEXT_KEY, DEFAULT_SAVE_CALLABLE_NAME,
                                POWDirDataSourceDirLoader, _DSD)
from PyOpenWorm.datasource_loader import LoadFailed
from PyOpenWorm.data_trans.data_with_evidence_ds import DataWithEvidenceDataSource as DWEDS
from PyOpenWorm.command_util import IVar, PropertyIVar
from PyOpenWorm.evidence import Evidence
from PyOpenWorm.document import Document
from PyOpenWorm.website import Website
from PyOpenWorm.contextDataObject import ContextDataObject
from .TestUtilities import noexit, stderr, stdout


class BaseTest(unittest.TestCase):
    def setUp(self):
        self.testdir = tempfile.mkdtemp(prefix=__name__ + '.')
        self.startdir = os.getcwd()
        os.chdir(self.testdir)
        self.cut = POW()

    def tearDown(self):
        os.chdir(self.startdir)
        shutil.rmtree(self.testdir)
        self.cut._disconnect()

    def _init_conf(self, conf=None):
        if not conf:
            conf = {}
        os.mkdir('.pow')
        with open(p('.pow', 'pow.conf'), 'w') as f:
            json.dump(conf, f)


class POWTest(BaseTest):

    def test_init_default_creates_store(self):
        self.cut.init()
        self.assertTrue(exists(p('.pow', 'worm.db')), msg='worm.db is created')

    def test_init_default_creates_config(self):
        self.cut.init()
        self.assertTrue(exists(p('.pow', 'pow.conf')), msg='pow.conf is created')

    def test_init_default_store_config_file_exists_no_change(self):
        self._init_conf()
        self.cut.init()
        with open(p('.pow', 'pow.conf'), 'r') as f:
            self.assertEqual('{}', f.read())

    def test_init_default_store_config_file_exists_update_store_conf(self):
        self._init_conf()

        self.cut.init(update_existing_config=True)
        with open(p('.pow', 'pow.conf'), 'r') as f:
            conf = json.load(f)
            self.assertEqual(conf['rdf.store_conf'], p('.pow', 'worm.db'), msg='path is updated')

    def test_fetch_graph_no_accessor_finder(self):
        with self.assertRaises(Exception):
            self.cut.fetch_graph("http://example.org/ImAGraphYesSiree")

    def test_fetch_graph_no_accessor(self):
        with self.assertRaises(UnreadableGraphException):
            self.cut.graph_accessor_finder = lambda url: None
            self.cut.fetch_graph("http://example.org/ImAGraphYesSiree")

    def test_init_fail_cleanup(self):
        ''' If we fail on init, there shouldn't be a .pow leftover '''
        self.cut.repository_provider = Mock()

        def failed_init(*args, **kwargs): raise _TestException('Oh noes!')
        self.cut.repository_provider.init.side_effect = failed_init
        try:
            self.cut.init()
            self.fail("Should have failed init")
        except _TestException:
            pass
        self.assertFalse(exists(self.cut.powdir), msg='powdir does not exist')

    def test_clone_fail_cleanup(self):
        ''' If we fail on clone, there shouldn't be a .pow leftover '''
        self.cut.repository_provider = Mock()

        def failed_clone(*args, **kwargs): raise _TestException('Oh noes!')
        self.cut.repository_provider.clone.side_effect = failed_clone
        try:
            self.cut.clone('ignored')
            self.fail("Should have failed clone")
        except _TestException:
            pass
        self.assertFalse(exists(self.cut.powdir), msg='powdir does not exist')

    def test_fetch_graph_with_accessor_success(self):
        m = Mock()
        self.cut.graph_accessor_finder = lambda url: m
        self.cut.fetch_graph("http://example.org/ImAGraphYesSiree")
        m.assert_called_with()

    def test_add_graph_success(self):
        m = Mock()
        q = (URIRef('http://example.org/s'),
             URIRef('http://example.org/p'),
             URIRef('http://example.org/o'),
             URIRef('http://example.org/c'))
        m().quads.return_value = [q]
        self._init_conf()

        self.cut.graph_accessor_finder = lambda url: m
        self.cut.add_graph("http://example.org/ImAGraphYesSiree")
        self.assertIn(q, self.cut._conf()['rdf.graph'])

    def test_conf_connection(self):
        self._init_conf()
        self.cut.config.user = True
        self.cut.config.set('key', '10')
        self.assertEqual(self.cut._conf()['key'], 10)

    def test_user_config_in_main_config(self):
        self._init_conf()
        self.cut.config.user = True
        self.cut.config.set('key', '10')
        self.assertEqual(self.cut._conf()['key'], 10)

    def test_conifg_set_get(self):
        self._init_conf()
        self.cut.config.set('key', '11')
        self.assertEqual(self.cut._conf()['key'], 11)

    def test_user_conifg_set_get_override(self):
        self._init_conf()
        self.cut.config.set('key', '11')
        self.cut.config.user = True
        self.cut.config.set('key', '10')
        self.assertEqual(self.cut._conf()['key'], 10)

    def test_context_set_config_get(self):
        c = 'http://example.org/context'
        self._init_conf()
        self.cut.context(c)
        self.assertEqual(self.cut.config.get(DATA_CONTEXT_KEY), c)

    def test_config_HERE_relative(self):
        '''
        $HERE should resolve relative to the user config file
        '''
        self._init_conf({'key': '$HERE/irrelevant'})
        conf = self.cut._conf()
        self.assertEqual(conf['key'], p(self.cut.powdir, 'irrelevant'))

    def test_user_config_HERE_relative(self):
        '''
        $HERE should resolve relative to the config file
        '''
        self._init_conf()
        userconfdir = p(self.testdir, 'userconf')
        os.mkdir(userconfdir)
        userconf = p(userconfdir, 'user.conf')
        self.cut.config = Mock()
        with open(userconf, 'w') as f:
            f.write('{"key": "$HERE/irrelevant"}')
        self.cut.config.user_config_file = userconf
        conf = self.cut._conf()
        self.assertEqual(conf['key'], p(userconfdir, 'irrelevant'))

    def test_config_HERE_relative_configured(self):
        '''
        $HERE should resolve relative to the config file
        '''
        userconfdir = p(self.testdir, 'movedconf')
        os.mkdir(userconfdir)
        userconf = p(userconfdir, 'pow.conf')
        with open(userconf, 'w') as f:
            f.write('{"key": "$HERE/irrelevant"}')
        self.cut.config_file = userconf
        conf = self.cut._conf()
        self.assertEqual(conf['key'], p(userconfdir, 'irrelevant'))

    def test_context_set_user_override(self):
        c = 'http://example.org/context'
        d = 'http://example.org/context_override'
        self._init_conf()
        self.cut.context(d, user=True)
        self.cut.context(c)
        self.assertEqual(self.cut.context(), d)

    def test_save_empty_attr_defaults(self):
        self._init_conf()
        with patch('importlib.import_module') as im:
            self.cut.save('tests.command_test_module', '', 'http://example.org/context')
            getattr(im(ANY), DEFAULT_SAVE_CALLABLE_NAME).assert_called()

    def test_save_attr(self):
        self._init_conf()
        with patch('importlib.import_module') as im:
            self.cut.save('tests.command_test_module', 'test', 'http://example.org/context')
            im(ANY).test.assert_called()

    def test_save_dotted_attr(self):
        self._init_conf()
        with patch('importlib.import_module') as im:
            self.cut.save('tests.command_test_module', 'test.test', 'http://example.org/context')
            im(ANY).test.test.assert_called()

    def test_save_no_attr(self):
        self._init_conf()
        with patch('importlib.import_module') as im:
            self.cut.save('tests.command_test_module', context='http://example.org/context')
            getattr(im(ANY), DEFAULT_SAVE_CALLABLE_NAME).assert_called()

    def test_save_data_context(self):
        a = 'http://example.org/mdc'
        self._init_conf({DATA_CONTEXT_KEY: a})
        with patch('importlib.import_module'):
            with patch('PyOpenWorm.command.Context') as ctxc:
                self.cut.save('tests.command_test_module')
                ctxc.assert_called_with(ident=a, conf=ANY)
                ctxc().save_context.assert_called()

    def test_save_validates_imports_fail(self):
        # add a statement with an object in another context
        # don't import context
        # expect exception
        with self.assertRaises(StatementValidationError):
            a = 'http://example.org/mdc'
            self._init_conf({DATA_CONTEXT_KEY: a})
            with patch('importlib.import_module') as im:
                def f(ns):
                    stmt = MagicMock()
                    stmt.context.identifier = URIRef(a)
                    ns.context.add_statement(stmt)
                im().test = f
                self.cut.save('tests', 'test')

    def test_save_validates_with_no_context_on_object(self):
        # add a statement with an uncontextualized object (e.g., a literal)
        # doesn't fail
        a = 'http://example.org/mdc'
        s = URIRef('http://example.org/node')
        self._init_conf({DATA_CONTEXT_KEY: a})
        with patch('importlib.import_module') as im:
            def f(ns):
                stmt = Mock()
                stmt.object.context = None
                stmt.to_triple.return_value = (s, s, s)
                stmt.property.context.identifier = URIRef(a)
                stmt.subject.context.identifier = URIRef(a)
                stmt.context.identifier = URIRef(a)
                ns.context.add_statement(stmt)
            im().test = f
            self.cut.save('tests', 'test')

    def test_save_validates_object_context_import_before_success(self):
        a = 'http://example.org/mdc'
        s = URIRef('http://example.org/node')
        self._init_conf({DATA_CONTEXT_KEY: a})
        with patch('importlib.import_module') as im:
            def f(ns):
                ctx = ns.context
                stmt = MagicMock(name='stmt')
                new_ctx = Mock(name='new_ctx')
                stmt.to_triple.return_value = (s, s, s)
                stmt.object.context.identifier = new_ctx.identifier
                stmt.property.context.identifier = URIRef(a)
                stmt.subject.context.identifier = URIRef(a)
                stmt.context.identifier = URIRef(a)

                ctx.add_import(new_ctx)
                ctx.add_statement(stmt)
            im().test = f
            self.cut.save('tests', 'test')

    def test_save_validates_import_after_success(self):
        a = 'http://example.org/mdc'
        s = URIRef('http://example.org/node')
        k = URIRef('http://example.org/new_ctx')
        self._init_conf({DATA_CONTEXT_KEY: a})
        with patch('importlib.import_module') as im:
            def f(ns):
                ctx = ns.context
                stmt = MagicMock(name='stmt')
                new_ctx = Mock(name='new_ctx')
                new_ctx.identifier = k
                stmt.to_triple.return_value = (s, s, s)
                stmt.object.context.identifier = k
                stmt.property.context.identifier = URIRef(a)
                stmt.subject.context.identifier = URIRef(a)
                stmt.context.identifier = URIRef(a)

                ctx.add_statement(stmt)
                ctx.add_import(new_ctx)
            im().test = f
            self.cut.save('tests', 'test')

    def test_save_validates_additional_context_saved_fails(self):
        # add a statement with an object in another context
        # define a context using the 'context factory' provided by the context with that context ID
        # validation should not succeed
        #
        # Usually don't test non-specified interactions, but this one seems relevant to clearly show the separation of
        # these features
        a = 'http://example.org/mdc'
        s = URIRef('http://example.org/node')
        self._init_conf({DATA_CONTEXT_KEY: a})
        with patch('importlib.import_module') as im:
            def f(ns):
                ctx = ns.context
                new_ctx = ns.new_context('http://example.org/nctx')
                stmt = MagicMock(name='stmt')
                stmt.to_triple.return_value = (s, s, s)
                stmt.object.context.identifier = new_ctx.identifier
                stmt.property.context.identifier = URIRef(a)
                stmt.subject.context.identifier = URIRef(a)
                stmt.context.identifier = URIRef(a)

                ctx.add_statement(stmt)
            im().test = f
            with self.assertRaises(StatementValidationError):
                self.cut.save('tests', 'test')

    def test_save_validation_fail_in_parent_precludes_save(self):
        a = 'http://example.org/mdc'
        s = URIRef('http://example.org/node')
        k = URIRef('http://example.org/unknown_ctx')
        self._init_conf({DATA_CONTEXT_KEY: a})
        with patch('importlib.import_module') as im:
            with patch('PyOpenWorm.command.Context') as ctxc:

                data_context = Mock()
                data_context.identifier = URIRef(a)

                ctxk = Mock()
                ctxk.identifier = k

                ctxc.side_effect = [data_context, ctxk]

                def f(ns):
                    ctx = ns.context
                    ns.new_context('this value doesnt matter')
                    stmt = MagicMock(name='stmt')
                    stmt.to_triple.return_value = (s, s, s)

                    stmt.object.context.identifier = URIRef(a)
                    stmt.property.context.identifier = k
                    stmt.subject.context.identifier = URIRef(a)
                    stmt.context.identifier = URIRef(a)

                    ctx.add_statement(stmt)

                im().test = f

                try:
                    self.cut.save('tests', 'test')
                    self.fail('Should have errored')
                except StatementValidationError:
                    data_context.save_context.assert_not_called()
                    ctxk.save_context.assert_not_called()

    def test_save_validation_fail_in_created_context_precludes_save(self):
        # Test that if validation fails in the parent, no other valid contexts are saved
        a = 'http://example.org/mdc'
        s = URIRef('http://example.org/node')
        k = URIRef('http://example.org/created_context')
        v = URIRef('http://example.org/unknown_context')
        self._init_conf({DATA_CONTEXT_KEY: a})
        with patch('importlib.import_module') as im:
            with patch('PyOpenWorm.command.Context') as ctxc:

                data_context = Mock()
                data_context.identifier = URIRef(a)

                ctxk = Mock()
                ctxk.identifier = k

                ctxc.side_effect = [data_context, ctxk]

                def f(ns):
                    ctx = ns.context
                    new_ctx = ns.new_context('this value doesnt matter')
                    stmt = MagicMock(name='stmt')
                    stmt.to_triple.return_value = (s, s, s)

                    stmt.object.context.identifier = URIRef(a)
                    stmt.property.context.identifier = URIRef(a)
                    stmt.subject.context.identifier = URIRef(a)
                    stmt.context.identifier = URIRef(a)
                    ctx.add_statement(stmt)

                    stmt1 = MagicMock(name='stmt')
                    stmt1.to_triple.return_value = (s, s, s)

                    stmt1.object.context.identifier = k
                    stmt1.property.context.identifier = v
                    stmt1.subject.context.identifier = k
                    stmt1.context.identifier = k

                    new_ctx.add_statement(stmt1)

                im().test = f

                try:
                    self.cut.save('tests', 'test')
                    self.fail('Should have errored')
                except StatementValidationError:
                    data_context.save_context.assert_not_called()
                    ctxk.save_context.assert_not_called()

    def test_save_returns_something(self):
        a = 'http://example.org/mdc'
        self._init_conf({DATA_CONTEXT_KEY: a})
        with patch('importlib.import_module'):
            self.assertIsNotNone(next(iter(self.cut.save('tests', 'test')), None))

    def test_save_returns_context(self):
        from PyOpenWorm.context import Context
        a = 'http://example.org/mdc'
        self._init_conf({DATA_CONTEXT_KEY: a})
        with patch('importlib.import_module'):
            self.assertIsInstance(next(self.cut.save('tests', 'test')), Context)

    def test_save_returns_created_contexts(self):
        a = 'http://example.org/mdc'
        b = 'http://example.org/smoo'
        self._init_conf({DATA_CONTEXT_KEY: a})
        with patch('importlib.import_module') as im:
            def f(ctx):
                ctx.new_context(b)

            im().test.side_effect = f
            self.assertEqual(set(x.identifier for x in self.cut.save('tests', 'test')), {URIRef(a), URIRef(b)})

    def test_save_saves_new_context(self):
        a = 'http://example.org/mdc'
        b = 'http://example.org/smoo'
        c = []
        self._init_conf({DATA_CONTEXT_KEY: a})
        with patch('importlib.import_module') as im, \
                patch('PyOpenWorm.command.Context'), \
                patch('PyOpenWorm.context.Context'):
            def f(ctx):
                c.append(ctx.new_context(b))

            im().test.side_effect = f
            self.cut.save('tests', 'test')
            c[0]._backer.save_context.assert_called()


class POWEvidenceGetDWEDSTest(unittest.TestCase):
    def setUp(self):
        self.parent = Mock(name='parent')
        self.cut = POWEvidence(self.parent)

        dweds = Mock(name='dweds', spec=DWEDS())
        # load from the given identifier is a dweds
        self.parent._data_ctx.stored(ANY).query().load.return_value = [dweds]
        # load evidence from the evidence_context is just one evidence object
        self.ev_load = dweds.evidence_context.stored(ANY).query().load

    def test_doc(self):
        # given
        evid = Mock(name='evidence')
        doc = Mock(name="doc", spec=Document())
        self.ev_load.return_value = [evid]
        evid.reference.return_value = doc

        # when
        self.cut.get(URIRef('http://example.org/context'))

        # then
        self.parent.message.assert_called()

    def test_no_evidence(self):
        '''
        There's no evidence, so we shouldn't see any output
        '''
        # given
        self.ev_load.return_value = []

        # when
        self.cut.get(URIRef('http://example.org/context'))

        # then
        self.parent.message.assert_not_called()


class POWEvidenceGetContextTest(unittest.TestCase):
    def setUp(self):
        self.parent = Mock(name='parent')
        self.cut = POWEvidence(self.parent)

    def test_doc(self):
        # given
        evid = Mock(name='evidence')
        doc = Mock(name="doc", spec=Document())
        cdo = Mock(name='cdo', spec=ContextDataObject())
        # load from the given identifier is a ContextDataObject
        self.parent._data_ctx.stored(ANY).query().load.side_effect = [[cdo],
                                                                      [evid]]
        evid.reference.return_value = doc

        # when
        self.cut.get(URIRef('http://example.org/context'))

        # then
        self.parent.message.assert_called()

    def test_web(self):
        # given
        evid = Mock(name='evidence')
        web = Mock(name="web", spec=Website())
        cdo = Mock(name='cdo', spec=ContextDataObject())
        # load from the given identifier is a ContextDataObject
        self.parent._data_ctx.stored(ANY).query().load.side_effect = [[cdo],
                                                                      [evid]]
        evid.reference.return_value = web

        # when
        self.cut.get(URIRef('http://example.org/context'))

        # then
        self.parent.message.assert_called()

    def test_no_evidence(self):
        '''
        There's no evidence, so we shouldn't see any output
        '''
        # given
        cdo = Mock(name='cdo', spec=ContextDataObject())
        self.parent._data_ctx.stored(ANY).query().load.side_effect = [[cdo],
                                                                      []]

        # when
        self.cut.get(URIRef('http://example.org/context'))

        # then
        self.parent.message.assert_not_called()


class POWTranslatorTest(unittest.TestCase):

    def test_translator_list(self):
        parent = Mock()
        dct = dict()
        dct['rdf.graph'] = Mock()
        parent._conf.return_value = dct
        # Mock the loading of DataObjects from the DataContext
        parent._data_ctx.stored(ANY)(conf=ANY).load.return_value = [Mock()]
        ps = POWTranslator(parent)

        self.assertIsNotNone(next(ps.list(), None))


class POWTranslateTest(BaseTest):

    def setUp(self):
        super(POWTranslateTest, self).setUp()
        os.mkdir('.pow')
        with open(p('.pow', 'pow.conf'), 'w') as f:
            f.write('{"data_context_id": "http://example.org/data"}')

    def test_translate_unknown_translator_message(self):
        '''
        Should exit with a message indicating the translator type
        cannot be found in the graph
        '''

        translator = 'http://example.org/translator'
        imports_context_ident = 'http://example.org/imports'
        with self.assertRaisesRegexp(GenericUserError, re.escape(translator)):
            self.cut.translate(translator, imports_context_ident)

    def test_translate_unknown_source_message(self):
        '''
        Should exit with a message indicating the source type cannot
        be found in the graph
        '''

        translator = 'http://example.org/translator'
        source = 'http://example.org/source'
        imports_context_ident = 'http://example.org/imports'
        self.cut._lookup_translator = lambda *args, **kwargs: Mock()
        with self.assertRaisesRegexp(GenericUserError, re.escape(source)):
            self.cut.translate(translator, imports_context_ident, data_sources=(source,))

    # Test saving a translator ensures the input and output types are saved source is saved


class IVarTest(unittest.TestCase):

    def test_property_doc(self):

        class A(object):
            @IVar.property
            def p(self):
                return 0

        self.assertEqual('', A.p.__doc__)

    def test_property_doc_no_args(self):

        class A(object):
            @IVar.property()
            def p(self):
                return 0
        self.assertEqual('', A.p.__doc__)

    def test_property_doc_match(self):

        class A(object):
            @IVar.property(doc='this')
            def p(self):
                return 0
        self.assertEqual('this', A.p.__doc__)

    def test_property_docstring_doc(self):

        class A(object):
            @IVar.property()
            def p(self):
                'this'
                return 0
        self.assertEqual('this', A.p.__doc__)

    def test_property_multiple_docs(self):

        class A(object):
            @IVar.property(doc='that')
            def p(self):
                'this'
                return 0
        self.assertEqual('this', A.p.__doc__)

    def test_property_doc_strip(self):

        class A(object):
            @IVar.property(doc='   this   ')
            def p(self):
                return 0
        self.assertEqual('this', A.p.__doc__)

    def test_property_doc_strip_docstring(self):

        class A(object):
            @IVar.property
            def p(self):
                '    this '
                return 0
        self.assertEqual('this', A.p.__doc__)

    def test_ivar_default(self):
        class A(object):
            p = IVar(3)

        self.assertEqual(A().p, 3)


class IVarPropertyTest(unittest.TestCase):

    def test_set_setter(self):
        iv = PropertyIVar()
        iv.value_setter = lambda target, val: None

        class A(object):
            p = iv
        a = A()
        a.p = 3

    def test_set_setter2(self):
        iv = PropertyIVar()

        class A(object):
            p = iv
        a = A()
        with self.assertRaises(AttributeError):
            a.p = 3


@mark.inttest
class GitCommandTest(BaseTest):

    def setUp(self):
        super(GitCommandTest, self).setUp()
        self.cut.repository_provider = GitRepoProvider()

    def test_init(self):
        """ A git directory should be created when we use the .git repository
           provider
        """
        self.cut.init()
        self.assertTrue(exists(p(self.cut.powdir, '.git')))

    def test_init_tracks_config(self):
        """ Test that the config file is tracked """
        self.cut.init()
        p(self.cut.powdir, '.git')

    def test_clone_creates_git_dir(self):
        self.cut.basedir = 'r1'
        self.cut.init()

        pd = self.cut.powdir

        clone = 'r2'
        self.cut.basedir = clone
        self.cut.clone(pd)
        self.assertTrue(exists(p('r2', '.pow', '.git')))

    def test_clones_graphs(self):
        self.cut.basedir = 'r1'
        self.cut.init()

        self._add_to_graph()
        self.cut.commit('Commit Message')

        pd = self.cut.powdir

        clone = 'r2'
        self.cut.basedir = clone
        self.cut.clone(pd)
        self.assertTrue(exists(p(self.cut.powdir, 'graphs', 'index')))

    def test_clones_config(self):
        self.cut.basedir = 'r1'
        self.cut.init()

        self._add_to_graph()
        self.cut.commit('Commit Message')

        pd = self.cut.powdir

        clone = 'r2'
        self.cut.basedir = clone
        self.cut.clone(pd)
        self.assertTrue(exists(self.cut.config_file))

    def test_clone_creates_store(self):
        self.cut.basedir = 'r1'
        self.cut.init()

        self._add_to_graph()
        self.cut.commit('Commit Message')

        pd = self.cut.powdir

        clone = 'r2'
        self.cut.basedir = clone
        self.cut.clone(pd)
        self.assertTrue(exists(self.cut.store_name), msg=self.cut.store_name)

    def test_reset_resets_add(self):
        self.cut.init()

        self._add_to_graph()
        # dirty up the index
        repo = git.Repo(self.cut.powdir)
        f = p(self.cut.powdir, 'something')
        open(f, 'w').close()

        self.cut.commit('Commit Message 1')

        repo.index.add(['something'])

        self.cut.commit('Commit Message 2')

        self.assertNotIn('something', [x[0] for x in repo.index.entries])

    def test_reset_resets_remove(self):
        self.cut.init()

        self._add_to_graph()
        # dirty up the index
        repo = git.Repo(self.cut.powdir)
        f = p(self.cut.powdir, 'something')
        open(f, 'w').close()

        self.cut.commit('Commit Message 1')

        repo.index.remove([p('graphs', 'index')])

        self.cut.commit('Commit Message 2')

        self.assertIn(p('graphs', 'index'), [x[0] for x in repo.index.entries])

    def _add_to_graph(self):
        m = Mock()
        q = (URIRef('http://example.org/s'),
             URIRef('http://example.org/p'),
             URIRef('http://example.org/o'),
             URIRef('http://example.org/c'))
        m().quads.return_value = [q]

        self.cut.graph_accessor_finder = lambda url: m
        self.cut.add_graph("http://example.org/ImAGraphYesSiree")


class CloneProgressTest(unittest.TestCase):
    def setUp(self):
        self.pr = Mock()
        self.pr.n = 0
        self.cp = _CloneProgress(self.pr)

    def test_progress(self):
        self.cp(1, 10)
        self.pr.update.assert_called_with(10)

    def test_progress_reset(self):
        self.pr.n = 3
        self.cp(2, 10)
        self.pr.update.assert_called_with(10)

    def test_progress_not_reset(self):
        self.pr.n = 5
        self.cp(0, 10)
        self.pr.update.assert_called_with(5)

    def test_progress_total(self):
        self.cp(0, 1, 11)
        self.assertEqual(self.pr.total, 11)

    def test_progress_no_unit(self):
        def f():
            raise AttributeError()
        pr = Mock()
        pr.unit.side_effect = f
        _CloneProgress(pr)


@mark.inttest
class ConfigTest(unittest.TestCase):

    def setUp(self):
        self.testdir = tempfile.mkdtemp(prefix=__name__ + '.')
        self.startdir = os.getcwd()
        os.chdir(self.testdir)

    def tearDown(self):
        os.chdir(self.startdir)
        shutil.rmtree(self.testdir)

    def test_set_new(self):
        parent = Mock()
        fname = p(self.testdir, 'test.conf')

        def f():
            with open(fname, 'w') as f:
                f.write('{}\n')
        parent._init_config_file.side_effect = f
        parent.config_file = fname
        parent.powdir = self.testdir
        cut = POWConfig(parent)
        cut.set('key', 'null')
        parent._init_config_file.assert_called()

    def test_set_get_new(self):
        parent = Mock()
        fname = p(self.testdir, 'test.conf')

        def f():
            with open(fname, 'w') as f:
                f.write('{}\n')
        parent._init_config_file.side_effect = f
        parent.config_file = fname
        parent.powdir = self.testdir
        cut = POWConfig(parent)
        cut.set('key', '1')
        self.assertEqual(cut.get('key'), 1)

    def test_set_new_user(self):
        parent = Mock()
        parent.powdir = self.testdir
        cut = POWConfig(parent)
        cut.user = True
        cut.set('key', '1')
        self.assertEqual(cut.get('key'), 1)

    def test_set_user_object(self):
        parent = Mock()
        parent.powdir = self.testdir
        cut = POWConfig(parent)
        cut.user = True
        cut.set('key', '{"smoop": "boop"}')
        self.assertEqual(cut.get('key'), {'smoop': 'boop'})


class POWSourceTest(unittest.TestCase):
    def test_list(self):
        parent = Mock()
        dct = dict()
        dct['rdf.graph'] = Mock()
        parent._conf.return_value = dct
        # Mock the loading of DataObjects from the DataContext
        parent._data_ctx.stored(ANY).query(conf=ANY).load.return_value = []
        ps = POWSource(parent)
        self.assertIsNone(next(ps.list(), None))

    def test_list_with_entry(self):
        parent = Mock()
        dct = dict()
        dct['rdf.graph'] = Mock()
        parent._conf.return_value = dct
        # Mock the loading of DataObjects from the DataContext
        parent._data_ctx.stored(ANY).query(conf=ANY).load.return_value = [Mock()]
        ps = POWSource(parent)

        self.assertIsNotNone(next(ps.list(), None))


class POWDSDLoaderNoIndex(unittest.TestCase):
    def setUp(self):
        self.testdir = tempfile.mkdtemp(prefix=__name__ + '.')

    def tearDown(self):
        shutil.rmtree(self.testdir)

    def test_no_index_can_load_false(self):
        "Test index of dsds doesn't exist yet -> should indicate with an exception"
        cut = POWDirDataSourceDirLoader(self.testdir)
        self.assertFalse(cut.can_load(Mock()))

    def test_no_index_load_failed(self):
        cut = POWDirDataSourceDirLoader(self.testdir)
        with self.assertRaisesRegexp(LoadFailed, re.escape(self.testdir)):
            cut.load(Mock())


class POWDSDLoaderMissingDSD(unittest.TestCase):
    def setUp(self):
        self.testdir = tempfile.mkdtemp(prefix=__name__ + '.')
        with open(p(self.testdir, 'index'), 'w') as f:
            print('dsdid1 dir1', file=f)
            print('dsdid2 dir2', file=f)

    def tearDown(self):
        shutil.rmtree(self.testdir)

    def test_dir_missing_can_load_false(self):
        '''
        If the directory pointed at by the index isn't there, then can_load should return false

        It may take some non-trivial amount of time to do the directory listing and check each entry exists, but we
        don't anticipate all that many in one repo
        '''
        cut = POWDirDataSourceDirLoader(self.testdir)
        self.assertFalse(cut.can_load('dsdid1'))

    def test_dir_missing_load(self):
        cut = POWDirDataSourceDirLoader(self.testdir)
        with self.assertRaises(LoadFailed):
            cut.load('dsdid1')

    def test_dir_removed_load_no_raise(self):
        '''
        The load method doesn't take responsibility for the directory existing, in general
        '''
        os.mkdir(p(self.testdir, 'dir1'))
        cut = POWDirDataSourceDirLoader(self.testdir)
        cut.load('dsdid1')
        os.rmdir(p(self.testdir, 'dir1'))
        cut.load('dsdid1')


class TestDSD(unittest.TestCase):

    def setUp(self):
        self.testdir = tempfile.mkdtemp(prefix=__name__ + '.')
        mc = [MagicMock()]
        mc[0].dirkey = 'dirkey'
        self.cut = _DSD(dict(), self.testdir, mc)
        self.mc = mc

    def test_dsd_create(self):
        '''
        Test directory for the dsdl doesn't exist yet AND loaders available
            -> should create the dir
        '''
        self.cut['dirkey']
        self.assertIn('dirkey', listdir(self.testdir))

    def test_index_dir_exists(self):
        '''
        Test directory for the dsdl exists
        '''
        os.makedirs(p(self.testdir, 'dirkey'))
        self.cut['dirkey']
        self.assertIn('dirkey', listdir(self.testdir))

    def test_no_loaders_key_error(self):
        '''
        Test no loaders can load the data source -> should present a key error
        '''
        self.mc[0]().can_load.return_value = False
        with self.assertRaises(KeyError):
            self.cut['not_there']

    # Test a loader that returns a directory outside of its assigned directory
    # Test a loader that returns a non-existant file
    # Test a loader that returns a non-directory

    # Don't have preferences yet
    # Test multiple loaders are ordered by preference -> should pick the highest ordered
    # Test multiple loaders are ordered by preference and most preferred fails -> should pick the next highest ordered


@mark.inttest
class POWAccTest(unittest.TestCase):
    ''' smoke-test for pow command line and the standard data base '''

    def setUp(self):
        import threading
        self.ns = threading.local()

    def set_up(self):
        self.ns.testdir = tempfile.mkdtemp(prefix=__name__ + '.')
        shutil.copytree('.pow', p(self.ns.testdir, '.pow'), symlinks=True)

    def tear_down(self):
        shutil.rmtree(self.ns.testdir)

    def sh(self, command, **kwargs):
        env = dict(os.environ)
        env['PYTHONPATH'] = self.ns.testdir
        return check_output(shlex.split(command), env=env, cwd=self.ns.testdir).decode('utf-8')

    @property
    def testdir(self):
        return self.ns.testdir

    def test_runner(self):
        import threading
        mytests = [getattr(self, x) for x in dir(self) if x.startswith('t_')]
        threads = []
        exceptions = [None] * len(mytests)
        barrier = threading.Semaphore()

        def test_exec(idx, test):
            def f():
                try:
                    self.set_up()
                except BaseException as e:
                    barrier.release()
                    exceptions[idx] = e
                    return

                try:
                    return test()
                except BaseException as e:
                    exceptions[idx] = e
                finally:
                    try:
                        self.tear_down()
                    finally:
                        barrier.release()
            return f

        for idx, k in enumerate(mytests):
            t = threading.Thread(target=test_exec(idx, k), name=k.__name__)
            threads.append(t)
            t.start()

        for m in mytests:
            barrier.acquire()

        for thr, test, exc in zip(threads, mytests, exceptions):
            thr.join()
            if exc is not None:
                raise exc

    def t_translator_list(self):
        ''' Test we have some translator '''
        self.assertRegexpMatches(self.sh('pow translator list'), r'<[^>]+>')

    def t_source_list(self):
        ''' Test we have some data source '''
        self.assertRegexpMatches(self.sh('pow source list'), r'<[^>]+>')

    def t_source_list_dweds(self):
        ''' Test listing of DWEDS '''
        out = self.sh('pow source list --kind :DataWithEvidenceDataSource')
        self.assertRegexpMatches(out, r'<[^>]+>')

    def t_save_diff(self):
        ''' Change something and make a diff '''
        modpath = p(self.testdir, 'test_module')
        os.mkdir(modpath)
        open(p(modpath, '__init__.py'), 'w').close()
        with open(p(modpath, 'command_test_save.py'), 'w') as out:
            print(r'''
from test_module.monkey import Monkey


def pow_data(ns):
    ns.context.add_import(Monkey.definition_context)
    ns.context(Monkey)(bananas=55)
''', file=out)

        with open(p(modpath, 'monkey.py'), 'w') as out:
            print(r'''
from PyOpenWorm.dataObject import DataObject, DatatypeProperty


class Monkey(DataObject):
    class_context = 'http://example.org/primate/monkey'

    bananas = DatatypeProperty()
    def identifier_augment(self):
        return type(self).rdf_namespace['paul']

    def defined_augment(self):
        return True


__yarom_mapped_classes__ = (Monkey,)
''', file=out)
        print(self.sh('pow save --module test_module.command_test_save'))
        self.assertRegexpMatches(self.sh('pow diff'), r'<[^>]+>')

    def t_manual_graph_edit_no_diff(self):
        '''
        Edit a context file and do a diff -- there shouldn't be any difference because we ignore such manual updates
        '''
        index = self.sh('cat ' + p('.pow', 'graphs', 'index'))
        fname = index.split('\n')[0].split(' ')[0]

        open(p(self.testdir, '.pow', 'graphs', fname), 'w').close() # truncate a graph's serialization

        self.assertRegexpMatches(self.sh('pow diff'), r'^$')

    def t_list_contexts(self):
        ''' Test we have some contexts '''
        self.assertRegexpMatches(self.sh('pow list_contexts'), r'^http://')


class _TestException(Exception):
    pass
