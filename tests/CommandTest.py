import unittest
try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock
import tempfile
import os
from os.path import exists, join as p
import shutil
import json
from rdflib.term import URIRef
from pytest import mark

import git
from PyOpenWorm.git_repo import GitRepoProvider, _CloneProgress
from PyOpenWorm.command import POW, UnreadableGraphException
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
        os.mkdir('.pow')
        with open(p('.pow', 'pow.conf'), 'w') as f:
            f.write('{}')

        self.cut.init()
        with open('.pow/pow.conf', 'r') as f:
            self.assertEqual('{}', f.read())

    def test_init_default_store_config_file_exists_update_store_conf(self):
        os.mkdir('.pow')
        with open('.pow/pow.conf', 'w') as f:
            f.write('{}')

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
        os.mkdir('.pow')
        with open('.pow/pow.conf', 'w') as f:
            json.dump({'rdf.store': 'default'}, f)
            f.flush()

        self.cut.graph_accessor_finder = lambda url: m
        self.cut.add_graph("http://example.org/ImAGraphYesSiree")
        self.assertIn(q, self.cut._conf()['rdf.graph'])


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


class _TestException(Exception):
    pass
