import unittest
try:
    from unittest.mock import Mock, ANY, patch
except ImportError:
    from mock import Mock, ANY, patch
import tempfile
import os
from os.path import exists, join as p
import shutil
import json
from rdflib.term import URIRef
from pytest import mark
import re

import git
from PyOpenWorm.git_repo import GitRepoProvider, _CloneProgress
from PyOpenWorm.command import (POW, UnreadableGraphException, GenericUserError,
                                POWConfig, POWSource, DATA_CONTEXT_KEY, DEFAULT_SAVE_CALLABLE_NAME)
from PyOpenWorm.command_util import IVar, PropertyIVar


class BaseTest(unittest.TestCase):
    def setUp(self):
        self.testdir = tempfile.mkdtemp(prefix=__name__ + '.')
        self.startdir = os.getcwd()
        os.chdir(self.testdir)
        self.cut = POW()

    def tearDown(self):
        os.chdir(self.startdir)
        shutil.rmtree(self.testdir)


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
        with open('.pow/pow.conf', 'r') as f:
            self.assertEqual('{}', f.read())

    def test_init_default_store_config_file_exists_update_store_conf(self):
        self._init_conf()

        self.cut.init(update_existing_config=True)
        with open('.pow/pow.conf', 'r') as f:
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

    def _init_conf(self, conf=None):
        if not conf:
            conf = {}
        os.mkdir('.pow')
        with open(p('.pow', 'pow.conf'), 'w') as f:
            json.dump(conf, f)

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


class POWTranslateTest(BaseTest):

    def setUp(self):
        super(POWTranslateTest, self).setUp()
        os.mkdir('.pow')
        with open('.pow/pow.conf', 'w') as f:
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
        self.assertTrue(exists('r2/.pow/.git'))

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
        for x in os.walk('.'):
            print(x)
        self.assertTrue(exists(self.cut.store_name), msg=self.cut.store_name)

    def test_reset_resets_add(self):
        self.cut.init()

        self._add_to_graph()
        # dirty up the index
        repo = git.Repo(self.cut.powdir)
        f = p(self.cut.powdir, 'something')
        with open(f, 'w'):
            pass

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
        with open(f, 'w'):
            pass

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
        parent._data_ctx().stored(ANY)(conf=ANY).load.return_value = []
        ps = POWSource(parent)
        self.assertIsNone(next(ps.list(), None))

    def test_list_(self):
        parent = Mock()
        dct = dict()
        dct['rdf.graph'] = Mock()
        parent._conf.return_value = dct
        # Mock the loading of DataObjects from the DataContext
        parent._data_ctx().stored(ANY)(conf=ANY).load.return_value = [Mock()]
        ps = POWSource(parent)
        self.assertIsNotNone(next(ps.list(), None))


class _TestException(Exception):
    pass
