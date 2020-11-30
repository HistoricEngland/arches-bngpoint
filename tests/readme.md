# Unit tests

This section of the application allows unit tests to be written for custom python components.

You should ensure that all tests complete when:
  1. you pull down a new version of the code. This ensures you are aware that you've pulled something that is breaking your code. 
  1. you push you commits back to the remote. It's a good habit to have as the tests will at some point be run prior to merge during PRs.

We are working to making it part of the PR process. Azure Pipelines has good support for `pytest` but not `django-nose` (based on `nosetest` and `unittest`), which Arches uses. Fortunately, `pytest` is able to handle tests written using `unittest`.

Therefore, unit testing on the developer machine is currently using the `python manage.py test` command. Azure Pipelines will use pytest so your tests must take account of those requirments.

## Running the unit test on developer machine

1. Ensure that the virtualenv is activated as you would for using `runserver`.
1. Run the following command `python manage.py test tests --pattern="test_*.py" --settings="tests.test_settings"`

This will traverse the project and execute any TestCase classes in files that follow the `test_*.py` naming pattern.


## Description of files

- **test_settings** - this settings file is used to override the settings.py so that the tests work correctly. Only one settings file can be used per unit test run.
- **base_test.py** - all test classes should inherit from the `WardenTestClass` in the file.
- **pytest.ini** - used for configuration when `pytest-django` is used instead of `django-nose` and `django.test`.

## Description of directories

Below lists the usage of the directories. They are pretty self explanitory but _special_ folders are noted.

- **datatypes** - All tests against datatypes should be put in here
- **functions** - All function tests should be put in here
- **fixtures** _(special)_ - 
   This fixtures directory contains fixed files used to support tests. This could be graph.json files, csv files for loading etc.
   - **ontologies** - contains ontology files that can be loaded during tests.
   - **resource_graphs** - contains model/graph files that can be loaded during tests.
   - **system_settings** - contains instances of system settings models and data that are loaded when the test database is built (see base_test.py)
- **results** - Used to receive any test output results files.

> **TIP**: _fixtures/systems_settings/System_Settings.json_ - Run the code below to update this from your database
>   ```cmd
>   (env) C:\Development\repos\warden-root\Warden> python manage.py packages -o save_system_settings -d tests/fixtures/system_settings
>   ```

> **NOTE**: _fixtures_ is a term that appears to have other meaning in python tests. Looks like some kind of dependancy injection but needs to be looked at further.

## Writing a tests

To test your code, create a new python file within the folder that describes the what is being tested (e.g. a new datatype should have a file called `test_mydatatypename.py`
should be placed in the `tests/datatypes` folder). The `test_*.py` nameing pattern is required by pytest, so don't vary it.

> **TIP**: If you need to create a new directory to test a new type of class or entity, make sure that you include an `__init__.py` file in that directory
> to make sure it is picked up as a module.

In the new file create a new test class that inherits from the WardenTestCase class and use the `setUpClass` and `tearDownClass` to prepare the class and anything required in the database.

Ensure that you use the `@pytest.mark.django_db` decorator to ensure that your class test function are able to access the django database when the test is run using pytest.

Then, within the class define the test functions, all of which will be run during the test.

See below for an example datatype test

```py
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
from arches.app.utils.data_management.resource_graphs.importer import import_graph as resource_graph_importer
from tests.base_test import WardenTestCase
from tests import test_settings

import pytest

@pytest.mark.django-db
class MyDatatypeTests(WardenTestCase):
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
        widget_path = os.path.join(test_settings.WARDEN_WIDGETS_LOCATION,'mydatatype.json')
        management.call_command("widget", operation="register", source=widget_path)

        # Load datatype
        datatype_path = os.path.join(test_settings.WARDEN_DATATYPES_LOCATION,'mydatatpye.py')
        management.call_command("datatype", operation="register", source=datatype_path)

        # Load a test model
        with open(os.path.join("tests/fixtures/resource_graphs/mydatatype_testmodel.json"), "r") as f:
            model_file = JSONDeserializer().deserialize(f)
            resource_graph_importer(model_file["graph"])

        # Set some model ids that I'm going to be using when creating/finding tiles and resources
        cls.my_test_model_graphid = '8b5c34f4-bd4a-11ea-bff8-4074e009096c'
        cls.mydatatype_test_nodegroupid = 'a2193dd8-bd4a-11ea-a07f-4074e009096c'
        cls.mydatatype_test_nodeid = 'a2193dd8-bd4a-11ea-a07f-4074e009096c'

        # activate graph
        test_graph = models.GraphModel.objects.get(pk=cls.my_test_model_graphid)
        test_graph.isactive = True
        test_graph.save()
        
        
        # Test values
        cls.valid_value     = 'abc123'
        cls.invalid_value   = '123abc'
        cls.random_string   = 'kkj2323'


    @classmethod
    def tearDownClass(cls):
        # empty the index
        delete_terms_index()
        delete_concepts_index()
        delete_search_index()
        delete_resource_relations_index()

        # if necessary I can clear the resources too
        #models.ResourceInstance.objects.all().delete()

    def test_save_value(self):
        '''
            Check that it saves
        '''
        # To save data you need to login with appropriate credentials
        login = self.client.login(username="admin", password="admin")
        self.test_resource = Resource(graph_id=self.my_test_model_graphid)
        
        tile = Tile(data={self.mydatatype_test_nodeid: self.valid_value}, nodegroup_id=self.mydatatype_test_nodegroupid)
        test_tile_id = tile.tileid
        self.test_resource.tiles.append(tile)

        try:
            self.test_resource_good_bng_value.save()
        except Exception as e:
            # If it unexpectantly raises an exception then fail the test immediately.
            self.fail(str(e))

        # Allow index to happen
        time.sleep(2)

        # If successfully saved then check the value is correct
        tile2 = models.TileModel.objects.get(pk=test_tile_id)
        saved_value = tile2.data[self.mydatatype_test_nodeid]
        self.assertEqual(saved_value, self.valid_value)
        
    def test_validate_value(self):
        '''
            Make sure a good value validates
        '''
        tile = Tile(data={self.bng_nodeid: self.valid_value}, nodegroup_id=self.mydatatype_test_nodegroupid)
        errors = tile.validate([])
        self.assertEqual(len(errors),0)

```

## Azure Build Pipelines

> The following link provides useful information on setting up a Python tests and capturing result and code coverage - https://docs.microsoft.com/en-us/azure/devops/pipelines/ecosystems/python?view=azure-devops

The automated build and test process is still being defined, using `pytest` rather than `django-nose` with `unittest` used by Arches.

In order to allow us to build a suitable build and test environment, the agent is a hosted Ubuntu 18.04 machine so that we can take advantage of being able to create the supporting services (Postgresql, Elasticsearch, etc.) quickly and correctly.

These agents also have preinstalled almost all libraries required by Arches, with the exception of `gdal` and `mime-support`.

This means that we simply need to:

1. define the Python version
1. start docker services using the test docker-compose file.
1. inject and load a version of arches repos and its pip requirements
1. run the Warden pip requirements
1. run the `pytest` process, collecting the junit/xunit results and the code coverage results (from `pytest-cov`)
1. publish the test results (they generate test case records)
1. publish the code coverage anaylsis in order to see how much of your python code the tests have touched.