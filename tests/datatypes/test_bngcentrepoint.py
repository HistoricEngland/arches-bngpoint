import json
import os
import time

from django.core import management

from arches.app.models import models
from arches.app.models.resource import Resource
from arches.app.models.tile import Tile,TileValidationError
from arches.app.search.mappings import (
    prepare_terms_index,
    delete_terms_index,
    prepare_concepts_index,
    delete_concepts_index,
    prepare_search_index,
    delete_search_index,
    prepare_resource_relations_index,
    delete_resource_relations_index,
)
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.utils.data_management.resource_graphs.importer import import_graph as resource_graph_importer
from arches.app.utils.exceptions import InvalidNodeNameException, MultipleNodesFoundException
from arches.app.utils.index_database import index_resources_by_type
from tests.base_test import WardenTestCase
from tests import test_settings

import pytest

@pytest.mark.django_db
class BngCentrePointTests(WardenTestCase):
    @classmethod
    def setUpClass(cls):
        # Rebuild the index for this test
        delete_terms_index()
        delete_concepts_index()
        delete_search_index()

        prepare_terms_index(create=True)
        prepare_concepts_index(create=True)
        prepare_search_index(create=True)
        prepare_resource_relations_index(create=True)

        # Clear out all resources
        models.ResourceInstance.objects.all().delete()

        #Load datatype's widget
        widget_path = os.path.join(test_settings.WARDEN_WIDGETS_LOCATION,'bngpoint.json')
        management.call_command("widget", operation="register", source=widget_path)

        # Load datatype
        datatype_path = os.path.join(test_settings.WARDEN_DATATYPES_LOCATION,'bngcentrepoint.py')
        management.call_command("datatype", operation="register", source=datatype_path)

        # Load a test model
        with open(os.path.join("tests/fixtures/resource_graphs/bngcentrepoint_datatype_testmodel.json"), "rU") as f:
            model_file = JSONDeserializer().deserialize(f)
            resource_graph_importer(model_file["graph"])

        cls.bng_model_graphid = '8b5c34f4-bd4a-11ea-bff8-4074e009096c'
        cls.bng_nodegroupid = 'a2193dd8-bd4a-11ea-a07f-4074e009096c'
        cls.bng_nodeid = 'a2193dd8-bd4a-11ea-a07f-4074e009096c'

        # activate graph
        test_graph = models.GraphModel.objects.get(pk=cls.bng_model_graphid)
        test_graph.isactive = True
        test_graph.save()


        # Test values
        cls.valid_bng     = 'SU1025169962'
        cls.invalid_bng   = 'S11025169962'
        cls.random_string = 'kkj23kj23d23'
        cls.bng_spaces = 'SU10251 6996'
        cls.fourchar_bng = 'SU16'


    @classmethod
    def tearDownClass(cls):
        delete_terms_index()
        delete_concepts_index()
        delete_search_index()
        delete_resource_relations_index()


    def test_save_bng_value(self):
        '''
            Check that it saves
        '''
        login = self.client.login(username="admin", password="admin")
        self.test_resource_good_bng_value = Resource(graph_id=self.bng_model_graphid)

        tile = Tile(data={self.bng_nodeid: self.valid_bng}, nodegroup_id=self.bng_nodegroupid)
        test_tile_id = tile.tileid
        self.test_resource_good_bng_value.tiles.append(tile)

        try:
            self.test_resource_good_bng_value.save()
        except Exception as e:
            self.fail(str(e))

        # Allow index to happen
        time.sleep(2)

        # If successfully saved then check the value is correct
        tile2 = models.TileModel.objects.get(pk=test_tile_id)
        bng_saved_value = tile2.data[self.bng_nodeid]
        self.assertEqual(bng_saved_value, self.valid_bng)

    def test_validate_good_bng_value(self):
        '''
            Make sure a good BNG validates
        '''
        tile = Tile(data={self.bng_nodeid: self.valid_bng}, nodegroup_id=self.bng_nodegroupid)
        errors = tile.validate([])
        self.assertEqual(len(errors),0)

    def test_validate_bad_bng_value(self):
        '''
            Make sure a BNG with correct length but wrong format fails validation
        '''
        tile = Tile(data={self.bng_nodeid: self.invalid_bng}, nodegroup_id=self.bng_nodegroupid)
        self.assertRaises(TileValidationError, tile.validate, None)

    def test_validate_random_string(self):
        '''
            Make sure a random string fails validation
        '''
        tile = Tile(data={self.bng_nodeid: self.random_string}, nodegroup_id=self.bng_nodegroupid)
        self.assertRaises(TileValidationError, tile.validate, None)


    def test_errors_with_spaces(self):
        '''
            Make sure a BNG with correct length but extra spaces fails validation
        '''
        tile = Tile(data={self.bng_nodeid: self.bng_spaces}, nodegroup_id=self.bng_nodegroupid)
        self.assertRaises(TileValidationError, tile.validate, None)

    def test_validates_short_4char_bng(self):
        '''
            Make sure a correct BNG with too few characters fails validation
        '''
        tile = Tile(data={self.bng_nodeid: self.fourchar_bng}, nodegroup_id=self.bng_nodegroupid)
        self.assertRaises(TileValidationError, tile.validate, None)



