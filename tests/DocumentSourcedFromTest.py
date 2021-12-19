from os.path import join as p
import json

import pytest
from rdflib.namespace import Namespace

from owmeta_core.datasource import DataSource
from owmeta_pytest_plugin import bundle_versions

from owmeta.document import SourcedFrom


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

    owm_project.sh(f'owm namespace bind ex {EX}')
    ctxid = owm.default_context.identifier
    owm_project.sh(
            f'owm contexts add-import {ctxid} http://schema.openworm.org/2020/07/sci',
            'owm declare owmeta.document:Document doi=10.1101/398370 --id=ex:doc',
            'owm declare test_module.asource:ASource'
            ' owmeta.document:SourcedFrom=ex:doc'
            ' --id=ex:ds',)

    owm = owm_project.owm()
    with owm.connect():
        ds = owm.default_context.stored(DataSource)(ident=EX['ds']).load_one()
        doc = ds.attach_property(SourcedFrom).one()
        assert doc.identifier == EX['doc']
