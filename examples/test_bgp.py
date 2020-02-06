"""
Examples of loading all information about an object or set of objects from the
database.
"""

from __future__ import absolute_import
from __future__ import print_function
import owmeta_core as P
from owmeta_core.context import Context

from owmeta.connection import Connection
from owmeta.neuron import Neuron


def pp_connection(conn):
    print(conn.pre_cell(), conn.post_cell(), conn.syntype(), conn.synclass(), conn.number())


with P.connect('default.conf') as owmconn:
    ctx = Context(ident="http://openworm.org/data", conf=owmconn.conf).stored
    query_object = ctx(Connection)(pre_cell=ctx(Neuron)(name='AVAL'))
    print('STARTING WITH AVAL')
    for x in query_object.load():
        pp_connection(x)
    print()
    print('STARTING WITH PVCL')
    query_object = ctx(Connection)(pre_cell=ctx(Neuron)(name='PVCL'))
    for x in query_object.load():
        pp_connection(x)

    print()
    print('NEURONS')
    query_object = ctx(Neuron)()
    # sometimes a neuron object with the same name is returned more than once
    names = dict()
    for x in query_object.load():
        n = x.name()
        if n not in names:
            names[n] = dict()
            print(n)
    print()
    print('NEIGHBORS of PVCL')
    query_object = ctx(Neuron)(name='PVCL')
    for x in query_object.neighbor():
        print(x.name())
    print()
    print('NEIGHBORS of AVAL with number=3 connections')
    query_object = ctx(Neuron)(name='AVAL')
    for x in query_object.neighbor.get(number=3):
        print(x.name())
    print
    print('NEURONS and their RECEPTORS')
    for x in ctx(Neuron)().load():
        # Wrap in a try-block in case there are no receptors listed
        print(x, end=' ')
        try:
            for r in x.receptor():
                print(' ', r, end=' ')
        except StopIteration:
            pass
        print()
