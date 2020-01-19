import pickle
from os import listdir, scandir, makedirs
from os.path import join as p, isdir

from pytest import fixture, fail, raises
from rdflib.plugins.memory import IOMemory
from rdflib.term import URIRef

from owmeta.lazy_deserialization_store import LazyDeserializationStore


def test_add_triple_make_new_pickle(tempdir):
    '''
    A new pickle should be created when a triple is added in a new context
    '''
    cut = LazyDeserializationStore(tempdir)
    cut.add((URIRef('http://example.org/1'),
             URIRef('http://example.org/2'),
             URIRef('http://example.org/3')),
            context=URIRef('http://example.org/ctx'))
    cut.commit()
    assert context_dir_count(tempdir) == 1


def test_remove_nonexistent_triple_makes_no_pickle(tempdir):
    '''
    No mutation. No pickle should be created
    '''
    cut = LazyDeserializationStore(tempdir)
    cut.remove((URIRef('http://example.org/1'),
                URIRef('http://example.org/2'),
                URIRef('http://example.org/3')),
               context=URIRef('http://example.org/ctx'))
    cut.commit()
    assert context_dir_count(tempdir) == 0


def test_add_remove_before_commit(tempdir):
    '''
    No pickle should be created when the context to pickle is empty
    '''
    cut = LazyDeserializationStore(tempdir)
    cut.add((URIRef('http://example.org/1'),
             URIRef('http://example.org/2'),
             URIRef('http://example.org/3')),
            context=URIRef('http://example.org/ctx'))
    cut.remove((URIRef('http://example.org/1'),
                URIRef('http://example.org/2'),
                URIRef('http://example.org/3')),
               context=URIRef('http://example.org/ctx'))
    cut.commit()
    assert context_dir_count(tempdir) == 0


def test_add_remove_triple(tempdir):
    '''
    A new pickle should be created when a triple is removed when already "active"
    '''
    cut = LazyDeserializationStore(tempdir)
    cut.add((URIRef('http://example.org/1'),
             URIRef('http://example.org/2'),
             URIRef('http://example.org/3')),
            context=URIRef('http://example.org/ctx'))
    cut.commit()
    cut.remove((URIRef('http://example.org/1'),
                URIRef('http://example.org/2'),
                URIRef('http://example.org/3')),
               context=URIRef('http://example.org/ctx'))
    cut.commit()
    dname = cut._format_context_directory_name(URIRef('http://example.org/ctx'))
    assert len(list(listdir(dname))) == 2


def test_triples_after_remove(tempdir):
    cut = LazyDeserializationStore(tempdir)
    cut.add((URIRef('http://example.org/1'),
             URIRef('http://example.org/2'),
             URIRef('http://example.org/3')),
            context=URIRef('http://example.org/ctx'))
    cut.commit()
    cut.remove((URIRef('http://example.org/1'),
                URIRef('http://example.org/2'),
                URIRef('http://example.org/3')),
               context=URIRef('http://example.org/ctx'))
    cut.commit()
    for trip, ctx in cut.triples((URIRef('http://example.org/1'),
                                  URIRef('http://example.org/2'),
                                  URIRef('http://example.org/3'))):
        fail("Should have no triples")


def test_triples_tentative(tempdir):
    cut = LazyDeserializationStore(tempdir)
    cut.add((URIRef('http://example.org/1'),
             URIRef('http://example.org/2'),
             URIRef('http://example.org/3')),
            context=URIRef('http://example.org/ctx'))
    for trip, ctx in cut.triples((URIRef('http://example.org/1'),
                                  URIRef('http://example.org/2'),
                                  URIRef('http://example.org/3')),
                                 context=URIRef('http://example.org/ctx')):
        break
    else: # no break
        fail("Should have triples")


def test_triples_committed_and_tentative(tempdir):
    cut = LazyDeserializationStore(tempdir)
    cut.add((URIRef('http://example.org/1'),
             URIRef('http://example.org/2'),
             URIRef('http://example.org/3')),
            context=URIRef('http://example.org/ctx'))
    cut.commit()
    cut.add((URIRef('http://example.org/1'),
             URIRef('http://example.org/2'),
             URIRef('http://example.org/3')),
            context=URIRef('http://example.org/ctx'))
    for trip, ctx in cut.triples((URIRef('http://example.org/1'),
                                  URIRef('http://example.org/2'),
                                  URIRef('http://example.org/3')),
                                 context=URIRef('http://example.org/ctx')):
        break
    else: # no break
        fail("Should have triples")


def test_triples_committed_and_tentative_remove(tempdir):
    cut = LazyDeserializationStore(tempdir)
    cut.add((URIRef('http://example.org/1'),
             URIRef('http://example.org/2'),
             URIRef('http://example.org/3')),
            context=URIRef('http://example.org/ctx'))
    cut.commit()
    cut.remove((URIRef('http://example.org/1'),
             URIRef('http://example.org/2'),
             URIRef('http://example.org/3')),
            context=URIRef('http://example.org/ctx'))
    for trip, ctx in cut.triples((URIRef('http://example.org/1'),
                                  URIRef('http://example.org/2'),
                                  URIRef('http://example.org/3')),
                                 context=URIRef('http://example.org/ctx')):
        fail("Should have no triples")


def test_load(tempdir):
    setup = LazyDeserializationStore(tempdir)
    setup.add((URIRef('http://example.org/1'),
             URIRef('http://example.org/2'),
             URIRef('http://example.org/3')),
            context=URIRef('http://example.org/ctx'))
    setup.commit()
    cut = LazyDeserializationStore(tempdir)
    for trip, ctx in cut.triples((URIRef('http://example.org/1'),
                                  URIRef('http://example.org/2'),
                                  URIRef('http://example.org/3')),
                                 context=URIRef('http://example.org/ctx')):
        break
    else:  # no break
        fail("Should have triples")


def test_load_triples_no_context(tempdir):
    setup = LazyDeserializationStore(tempdir)
    setup.add((URIRef('http://example.org/1'),
             URIRef('http://example.org/2'),
             URIRef('http://example.org/3')),
            context=URIRef('http://example.org/ctx'))
    setup.commit()
    cut = LazyDeserializationStore(tempdir)
    for trip, ctx in cut.triples((URIRef('http://example.org/1'),
                                  URIRef('http://example.org/2'),
                                  URIRef('http://example.org/3'))):
        break
    else:  # no break
        fail("Should have triples")


def test_load_triples_add_remove_no_context(tempdir):
    setup = LazyDeserializationStore(tempdir)
    setup.add((URIRef('http://example.org/1'),
             URIRef('http://example.org/2'),
             URIRef('http://example.org/3')),
            context=URIRef('http://example.org/ctx'))
    setup.commit()
    setup.remove((URIRef('http://example.org/1'),
             URIRef('http://example.org/2'),
             URIRef('http://example.org/3')),
            context=URIRef('http://example.org/ctx'))
    setup.commit()
    cut = LazyDeserializationStore(tempdir)
    for trip, ctx in cut.triples((URIRef('http://example.org/1'),
                                  URIRef('http://example.org/2'),
                                  URIRef('http://example.org/3'))):
        fail("Should have no triples")


def test_load_triples_add_remove_query_others(tempdir):
    setup = LazyDeserializationStore(tempdir)
    setup.add((URIRef('http://example.org/1'),
               URIRef('http://example.org/2'),
               URIRef('http://example.org/3')),
              context=URIRef('http://example.org/ctx'))
    setup.commit()
    setup.add((URIRef('http://example.org/1'),
               URIRef('http://example.org/2'),
               URIRef('http://example.org/4')),
              context=URIRef('http://example.org/ctx'))
    setup.commit()

    setup.add((URIRef('http://example.org/1'),
               URIRef('http://example.org/2'),
               URIRef('http://example.org/5')),
              context=URIRef('http://example.org/ctx'))
    setup.commit()

    setup.remove((URIRef('http://example.org/1'),
                  URIRef('http://example.org/2'),
                  URIRef('http://example.org/4')),
                 context=URIRef('http://example.org/ctx'))
    setup.commit()

    cut = LazyDeserializationStore(tempdir)
    for trip, ctx in cut.triples((URIRef('http://example.org/1'),
                                  URIRef('http://example.org/2'),
                                  URIRef('http://example.org/3'))):
        break
    else: # no break
        fail("Should have triples")


def test_load_triples_add_remove_10_no_context(tempdir):
    '''
    This is a check on the sorting of updates -- ensure that we're sorting numerically
    rather than alphanumerically. This is why we need 10 entries -- need to ensure 10 is
    sorted after 2
    '''
    setup = LazyDeserializationStore(tempdir)
    setup.add((URIRef('http://example.org/1'),
               URIRef('http://example.org/2'),
               URIRef('http://example.org/3')),
              context=URIRef('http://example.org/ctx'))
    setup.commit()
    setup.add((URIRef('http://example.org/1'),
               URIRef('http://example.org/2'),
               URIRef('http://example.org/4')),
              context=URIRef('http://example.org/ctx'))
    setup.commit()

    dname = setup._format_context_directory_name(URIRef('http://example.org/ctx'))
    assert '2.a.pickle' in listdir(dname)

    for x in range(7):
        setup.add((URIRef('http://example.org/1'),
                   URIRef('http://example.org/2'),
                   URIRef('http://example.org/' + str(5 + x))),
                  context=URIRef('http://example.org/ctx'))
        setup.commit()

    setup.remove((URIRef('http://example.org/1'),
                  URIRef('http://example.org/2'),
                  URIRef('http://example.org/4')),
                 context=URIRef('http://example.org/ctx'))
    setup.commit()
    assert '10.r.pickle' in listdir(dname)
    cut = LazyDeserializationStore(tempdir)
    for trip, ctx in cut.triples((URIRef('http://example.org/1'),
                                  URIRef('http://example.org/2'),
                                  URIRef('http://example.org/4'))):
        fail("Should have no triples")


def test_load_triples_add_remove_10_with_context(tempdir):
    '''
    This is the same as test_load_triples_add_remove_10_no_context, but we specify the
    context in the query.
    '''
    setup = LazyDeserializationStore(tempdir)
    setup.add((URIRef('http://example.org/1'),
               URIRef('http://example.org/2'),
               URIRef('http://example.org/3')),
              context=URIRef('http://example.org/ctx'))
    setup.commit()
    setup.add((URIRef('http://example.org/1'),
               URIRef('http://example.org/2'),
               URIRef('http://example.org/4')),
              context=URIRef('http://example.org/ctx'))
    setup.commit()

    dname = setup._format_context_directory_name(URIRef('http://example.org/ctx'))
    assert '2.a.pickle' in listdir(dname)

    for x in range(7):
        setup.add((URIRef('http://example.org/1'),
                   URIRef('http://example.org/2'),
                   URIRef('http://example.org/' + str(5 + x))),
                  context=URIRef('http://example.org/ctx'))
        setup.commit()

    setup.remove((URIRef('http://example.org/1'),
                  URIRef('http://example.org/2'),
                  URIRef('http://example.org/4')),
                 context=URIRef('http://example.org/ctx'))
    setup.commit()
    assert '10.r.pickle' in listdir(dname)
    cut = LazyDeserializationStore(tempdir)
    for trip, ctx in cut.triples((URIRef('http://example.org/1'),
                                  URIRef('http://example.org/2'),
                                  URIRef('http://example.org/4')),
                                 context=URIRef('http://example.org/ctx')):
        fail("Should have no triples")


def test_ignore_extraneous_dir_in_base(tempdir):
    makedirs(p(tempdir, 'whatsup'))
    setup = LazyDeserializationStore(tempdir)
    setup.add((URIRef('http://example.org/1'),
             URIRef('http://example.org/2'),
             URIRef('http://example.org/3')),
            context=URIRef('http://example.org/ctx'))
    setup.commit()
    cut = LazyDeserializationStore(tempdir)
    for trip, ctx in cut.triples((URIRef('http://example.org/1'),
                                  URIRef('http://example.org/2'),
                                  URIRef('http://example.org/3'))):
        pass


def test_ignore_extraneous_pickle(tempdir):
    setup = LazyDeserializationStore(tempdir)
    setup.add((URIRef('http://example.org/1'),
             URIRef('http://example.org/2'),
             URIRef('http://example.org/3')),
            context=URIRef('http://example.org/ctx'))
    setup.commit()
    dname = setup._format_context_directory_name(URIRef('http://example.org/ctx'))
    with open(p(dname, 'spooky'), 'wb') as f:
        f.write(b'gibberish')
    cut = LazyDeserializationStore(tempdir)
    for trip, ctx in cut.triples((URIRef('http://example.org/1'),
                                  URIRef('http://example.org/2'),
                                  URIRef('http://example.org/3'))):
        pass


def test_error_on_malformed_pickle(tempdir):
    setup = LazyDeserializationStore(tempdir)
    dname = setup._format_context_directory_name(URIRef('http://example.org/ctx'))
    makedirs(dname)
    with open(p(dname, '1.a.pickle'), 'wb') as f:
        f.write(b'gibberish')
    cut = LazyDeserializationStore(tempdir)

    with raises(pickle.UnpicklingError):
        for trip, ctx in cut.triples((URIRef('http://example.org/1'),
                                      URIRef('http://example.org/2'),
                                      URIRef('http://example.org/3'))):
            pass


def test_remove_after_load_creates_pickle(tempdir):
    '''
    When we do a remove, we check the active store for the triples before adding to
    tentative removals. If we don't load before this check, then we'll find no matching
    entries for the removal, so we won't create a pickle for it
    '''
    setup = LazyDeserializationStore(tempdir)
    setup.add((URIRef('http://example.org/1'),
               URIRef('http://example.org/2'),
               URIRef('http://example.org/3')),
              context=URIRef('http://example.org/ctx'))
    setup.commit()
    cut = LazyDeserializationStore(tempdir)
    cut.remove((URIRef('http://example.org/1'),
                URIRef('http://example.org/2'),
                URIRef('http://example.org/3')),
               context=URIRef('http://example.org/ctx'))
    cut.commit()
    dname = setup._format_context_directory_name(URIRef('http://example.org/ctx'))
    assert len(list(listdir(dname))) == 2


def test_collapse_empty(tempdir):
    '''
    Add and remove the same triple. After collapse, we should not have any revisions
    '''
    setup0 = LazyDeserializationStore(tempdir)
    setup0.add((URIRef('http://example.org/1'),
                URIRef('http://example.org/2'),
                URIRef('http://example.org/3')),
               context=URIRef('http://example.org/ctx'))
    setup0.commit()
    setup1 = LazyDeserializationStore(tempdir)
    setup1.remove((URIRef('http://example.org/1'),
                   URIRef('http://example.org/2'),
                   URIRef('http://example.org/3')),
                  context=URIRef('http://example.org/ctx'))
    setup1.commit()

    cut = LazyDeserializationStore(tempdir)
    cut.collapse('http://example.org/ctx')
    cut.commit()

    dname = cut._format_context_directory_name(URIRef('http://example.org/ctx'))
    assert len(list(listdir(dname))) == 0


def test_collapse_non_empty(tempdir):
    '''
    Add and a couple revisions. After collapse, we should have one revision
    '''
    setup0 = LazyDeserializationStore(tempdir)
    setup0.add((URIRef('http://example.org/1'),
                URIRef('http://example.org/2'),
                URIRef('http://example.org/3')),
               context=URIRef('http://example.org/ctx'))
    setup0.commit()
    setup1 = LazyDeserializationStore(tempdir)
    setup1.add((URIRef('http://example.org/1'),
                URIRef('http://example.org/2'),
                URIRef('http://example.org/4')),
               context=URIRef('http://example.org/ctx'))
    setup1.commit()

    cut = LazyDeserializationStore(tempdir)
    cut.collapse('http://example.org/ctx')
    cut.commit()

    dname = cut._format_context_directory_name(URIRef('http://example.org/ctx'))
    assert len(list(x for x in scandir(dname) if x.is_file())) == 1


def test_recover_prepared(tempdir):
    # If we prepare a commit, but fail in the middle of it, we should be able to restart
    # it
    setup = LazyDeserializationStore(tempdir)
    setup.add((URIRef('http://example.org/1'),
             URIRef('http://example.org/2'),
             URIRef('http://example.org/3')),
            context=URIRef('http://example.org/ctx'))
    setup.add((URIRef('http://example.org/1'),
             URIRef('http://example.org/7'),
             URIRef('http://example.org/8')),
            context=URIRef('http://example.org/ctx2'))
    setup.commit()

    setup.add((URIRef('http://example.org/1'),
             URIRef('http://example.org/4'),
             URIRef('http://example.org/5')),
            context=URIRef('http://example.org/ctx2'))
    setup.tpc_prepare()
    setup.tpc_abort()

    cut = LazyDeserializationStore(tempdir)
    for m in cut.triples((URIRef('http://example.org/1'),
                          URIRef('http://example.org/4'),
                          URIRef('http://example.org/5')),
                         context=URIRef('http://example.org/ctx2')):
        fail()


def test_abort_prepared(tempdir):
    # If we prepare a commit, but fail in the middle of it, we should be able to restart
    # it
    setup = LazyDeserializationStore(tempdir)
    setup.add((URIRef('http://example.org/1'),
             URIRef('http://example.org/2'),
             URIRef('http://example.org/3')),
            context=URIRef('http://example.org/ctx'))
    setup.add((URIRef('http://example.org/1'),
             URIRef('http://example.org/7'),
             URIRef('http://example.org/8')),
            context=URIRef('http://example.org/ctx2'))
    setup.commit()

    setup.add((URIRef('http://example.org/1'),
             URIRef('http://example.org/4'),
             URIRef('http://example.org/5')),
            context=URIRef('http://example.org/ctx2'))
    setup.tpc_prepare()
    setup.tpc_abort()

    cut = LazyDeserializationStore(tempdir)
    for m in cut.triples((URIRef('http://example.org/1'),
                          URIRef('http://example.org/4'),
                          URIRef('http://example.org/5')),
                         context=URIRef('http://example.org/ctx2')):
        fail()

    for m in cut.triples((URIRef('http://example.org/1'),
                          URIRef('http://example.org/7'),
                          URIRef('http://example.org/8')),
                         context=URIRef('http://example.org/ctx2')):
        break
    else:
        fail()


def test_abort_empty(tempdir):
    LazyDeserializationStore(tempdir).tpc_abort()


def test_commit_abort(tempdir):
    cut = LazyDeserializationStore(tempdir)
    cut.add((URIRef('http://example.org/1'),
             URIRef('http://example.org/2'),
             URIRef('http://example.org/3')),
            context=URIRef('http://example.org/ctx'))
    cut.commit()

    LazyDeserializationStore(tempdir).tpc_abort()


def test_commit_nothing(tempdir):
    LazyDeserializationStore(tempdir).tpc_commit()


def test_prepare_commit_commit(tempdir):
    cut = LazyDeserializationStore(tempdir)
    cut.add((URIRef('http://example.org/1'),
             URIRef('http://example.org/2'),
             URIRef('http://example.org/3')),
            context=URIRef('http://example.org/ctx'))
    cut.tpc_prepare()
    cut.tpc_commit()
    cut.tpc_commit()


def test_new_context_earliest_revision_None_for_uncommitted(tempdir):
    cut = LazyDeserializationStore(tempdir)
    cut.add((URIRef('http://example.org/1'),
             URIRef('http://example.org/2'),
             URIRef('http://example.org/3')),
            context=URIRef('http://example.org/ctx'))
    assert cut.earliest_revision(URIRef('http://example.org/ctx')) is None


def test_new_context_latest_revision_None_for_uncommitted(tempdir):
    cut = LazyDeserializationStore(tempdir)
    cut.add((URIRef('http://example.org/1'),
             URIRef('http://example.org/2'),
             URIRef('http://example.org/3')),
            context=URIRef('http://example.org/ctx'))
    assert cut.latest_revision(URIRef('http://example.org/ctx')) is None


def test_new_context_latest_revision_one(tempdir):
    cut = LazyDeserializationStore(tempdir)
    cut.add((URIRef('http://example.org/1'),
             URIRef('http://example.org/2'),
             URIRef('http://example.org/3')),
            context=URIRef('http://example.org/ctx'))
    cut.commit()
    assert cut.latest_revision(URIRef('http://example.org/ctx')) == 1


def test_new_context_earliest_revision_one(tempdir):
    cut = LazyDeserializationStore(tempdir)
    cut.add((URIRef('http://example.org/1'),
             URIRef('http://example.org/2'),
             URIRef('http://example.org/3')),
            context=URIRef('http://example.org/ctx'))
    cut.commit()
    assert cut.earliest_revision(URIRef('http://example.org/ctx')) == 1


def test_two_contexts_earliest_revision_one(tempdir):
    cut = LazyDeserializationStore(tempdir)
    cut.add((URIRef('http://example.org/1'),
             URIRef('http://example.org/2'),
             URIRef('http://example.org/3')),
            context=URIRef('http://example.org/ctx'))
    cut.commit()
    cut.add((URIRef('http://example.org/1'),
             URIRef('http://example.org/5'),
             URIRef('http://example.org/3')),
            context=URIRef('http://example.org/ctx'))
    cut.commit()
    assert cut.earliest_revision(URIRef('http://example.org/ctx')) == 1


def test_two_contexts_latest_revision_two(tempdir):
    cut = LazyDeserializationStore(tempdir)
    cut.add((URIRef('http://example.org/1'),
             URIRef('http://example.org/2'),
             URIRef('http://example.org/3')),
            context=URIRef('http://example.org/ctx'))
    cut.commit()
    cut.add((URIRef('http://example.org/1'),
             URIRef('http://example.org/5'),
             URIRef('http://example.org/3')),
            context=URIRef('http://example.org/ctx'))
    cut.commit()
    assert cut.latest_revision(URIRef('http://example.org/ctx')) == 2


def test_collapse_one_earliest_revision_two(tempdir):
    cut = LazyDeserializationStore(tempdir)
    cut.add((URIRef('http://example.org/1'),
             URIRef('http://example.org/2'),
             URIRef('http://example.org/3')),
            context=URIRef('http://example.org/ctx'))
    cut.commit()
    cut.collapse(URIRef('http://example.org/ctx'))
    cut.commit()
    assert cut.earliest_revision(URIRef('http://example.org/ctx')) == 2


def test_contexts_empty(tempdir):
    cut = LazyDeserializationStore(tempdir)

    assert set(cut.contexts()) == set()


def test_contexts_one_uncommitted(tempdir):
    cut = LazyDeserializationStore(tempdir)
    cut.add((URIRef('http://example.org/1'),
             URIRef('http://example.org/2'),
             URIRef('http://example.org/3')),
            context=URIRef('http://example.org/ctx'))

    assert set(cut.contexts()) == set([URIRef('http://example.org/ctx')])


def test_contexts_empty_by_add_remove_uncommitted(tempdir):
    cut = LazyDeserializationStore(tempdir)
    cut.add((URIRef('http://example.org/1'),
             URIRef('http://example.org/2'),
             URIRef('http://example.org/3')),
            context=URIRef('http://example.org/ctx'))
    cut.remove((URIRef('http://example.org/1'),
             URIRef('http://example.org/2'),
             URIRef('http://example.org/3')),
            context=URIRef('http://example.org/ctx'))

    assert set(cut.contexts()) == set()


def test_contexts_add_mult_remove_uncommitted(tempdir):
    cut = LazyDeserializationStore(tempdir)
    cut.add((URIRef('http://example.org/1'),
             URIRef('http://example.org/2'),
             URIRef('http://example.org/3')),
            context=URIRef('http://example.org/ctx'))
    cut.add((URIRef('http://example.org/1'),
             URIRef('http://example.org/2'),
             URIRef('http://example.org/4')),
            context=URIRef('http://example.org/ctx'))
    cut.remove((URIRef('http://example.org/1'),
                URIRef('http://example.org/2'),
                URIRef('http://example.org/3')),
               context=URIRef('http://example.org/ctx'))

    assert set(cut.contexts()) == set([URIRef('http://example.org/ctx')])


def test_add_remove_empty_committed(tempdir):
    cut = LazyDeserializationStore(tempdir)
    cut.add((URIRef('http://example.org/1'),
             URIRef('http://example.org/2'),
             URIRef('http://example.org/3')),
            context=URIRef('http://example.org/ctx'))
    cut.commit()
    cut.remove((URIRef('http://example.org/1'),
             URIRef('http://example.org/2'),
             URIRef('http://example.org/3')),
            context=URIRef('http://example.org/ctx'))
    cut.commit()

    assert set(cut.contexts()) == set()


def test_committed_context(tempdir):
    cut = LazyDeserializationStore(tempdir)
    cut.add((URIRef('http://example.org/1'),
             URIRef('http://example.org/2'),
             URIRef('http://example.org/3')),
            context=URIRef('http://example.org/ctx'))
    cut.commit()

    assert set(cut.contexts()) == set([URIRef('http://example.org/ctx')])


def test_deactivate(tempdir):
    cut = LazyDeserializationStore({
        'base_directory': tempdir,
        'max_active_contexts': 1
    })
    cut.add((URIRef('http://example.org/1'),
             URIRef('http://example.org/2'),
             URIRef('http://example.org/3')),
            context=URIRef('http://example.org/ctx'))
    cut.add((URIRef('http://example.org/1'),
             URIRef('http://example.org/2'),
             URIRef('http://example.org/3')),
            context=URIRef('http://example.org/ctx0'))
    cut.add((URIRef('http://example.org/1'),
             URIRef('http://example.org/4'),
             URIRef('http://example.org/3')),
            context=URIRef('http://example.org/ctx1'))

    cut.commit()

    assert len(cut.active_stores) == 1


def test_reactivate(tempdir):
    cut = LazyDeserializationStore({
        'base_directory': tempdir,
        'max_active_contexts': 1
    })
    cut.add((URIRef('http://example.org/1'),
             URIRef('http://example.org/2'),
             URIRef('http://example.org/3')),
            context=URIRef('http://example.org/ctx'))
    cut.add((URIRef('http://example.org/1'),
             URIRef('http://example.org/2'),
             URIRef('http://example.org/3')),
            context=URIRef('http://example.org/ctx0'))
    cut.add((URIRef('http://example.org/1'),
             URIRef('http://example.org/4'),
             URIRef('http://example.org/3')),
            context=URIRef('http://example.org/ctx1'))

    cut.commit()

    assert len(list(cut.triples((None, None, None), URIRef('http://example.org/ctx0')))) == 1


def test_reactivate_all_contexts(tempdir):
    cut = LazyDeserializationStore({
        'base_directory': tempdir,
        'max_active_contexts': 1
    })
    cut.add((URIRef('http://example.org/1'),
             URIRef('http://example.org/2'),
             URIRef('http://example.org/3')),
            context=URIRef('http://example.org/ctx'))
    cut.add((URIRef('http://example.org/1'),
             URIRef('http://example.org/2'),
             URIRef('http://example.org/3')),
            context=URIRef('http://example.org/ctx0'))
    cut.add((URIRef('http://example.org/1'),
             URIRef('http://example.org/4'),
             URIRef('http://example.org/3')),
            context=URIRef('http://example.org/ctx1'))

    cut.commit()

    assert len(list(cut.triples((None, None, None)))) == 3


def context_dir_count(tempdir):
    return len([x for x in listdir(tempdir) if isdir(p(tempdir, x))])
