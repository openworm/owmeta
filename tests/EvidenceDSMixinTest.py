from os.path import join as p
import json

import pytest
from rdflib.namespace import Namespace

from owmeta_core.datasource import DataSource
from owmeta_pytest_plugin import bundle_versions


EX = Namespace('http://example.org/')


@pytest.mark.inttest
@bundle_versions('owmeta_schema_bundle', [3])
@pytest.mark.bundle_remote('ow')
def test_augment_cmd_load(owmeta_schema_bundle, owm_project):
    owm_project.fetch(owmeta_schema_bundle)
    owm = owm_project.owm()
    deps = [{'id': owmeta_schema_bundle.id, 'version': owmeta_schema_bundle.version}]
    owm.config.set('dependencies', json.dumps(deps))

    modpath = owm_project.make_module('test_module')
    owm_project.writefile(p(modpath, 'asource.py'),
            'tests/test_modules/evidence_ds_mixin_source.py')
    owm_project.sh('owm save test_module.asource')

    with owm_project.owm().connect() as conn:
        conn.rdf.namespace_manager.bind('ex', EX)

    owm_project.sh(
            'owm declare owmeta.document:Document doi=10.1101/398370 --id=ex:doc')
    with owm_project.owm().connect() as conn:
        print(conn.rdf.serialize(format='n3').decode('utf-8'))
    owm_project.sh(
            'owm declare owmeta.evidence:Evidence reference=ex:doc'
            '    rdfs_comment="This says some stuff" --id=ex:ev',
            'owm declare test_module.asource:ASource a="Some arbitrary value" --id=ex:ds',
            'owm source attach-evidence ex:ds ex:ev')

    owm = owm_project.owm()
    with owm.connect():
        ds = list(owm.default_context(DataSource)(ident=EX['ds']).load())
        ev = ds.attached_evidence.one()
        assert ev.identifier == EX['ev']
