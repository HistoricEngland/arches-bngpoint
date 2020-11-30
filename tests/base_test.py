import os
from django.test import TestCase
from arches.app.models.graph import Graph
from arches.app.models.models import Ontology
from arches.app.search.search import SearchEngine
from arches.app.search.search_engine_factory import SearchEngineFactory
from arches.app.models.system_settings import settings
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.utils.data_management.resource_graphs.importer import import_graph as ResourceGraphImporter
from arches.app.utils.data_management.resources.importer import BusinessDataImporter
from tests import test_settings
from django.db import connection
from django.contrib.auth.models import User
from django.core import management

# these tests can be run from the command line via
# python manage.py test tests --pattern="*.py" --settings="tests.test_settings"

OAUTH_CLIENT_ID = "AAac4uRQSqybRiO6hu7sHT50C4wmDp9fAmsPlCj9"
OAUTH_CLIENT_SECRET = "7fos0s7qIhFqUmalDI1QiiYj0rAtEdVMY4hYQDQjOxltbRCBW3dIydOeMD4MytDM9ogCPiYFiMBW6o6ye5bMh5dkeU7pg1cH86wF6B\
        ap9Ke2aaAZaeMPejzafPSj96ID"
CREATE_TOKEN_SQL = """
        INSERT INTO public.oauth2_provider_accesstoken(
            token, expires, scope, application_id, user_id, created, updated)
            VALUES ('{token}', '1-1-2068', 'read write', 44, {user_id}, '1-1-2018', '1-1-2018');
    """


def setUpTestPackage():
    """
    see https://nose.readthedocs.io/en/latest/writing_tests.html#test-packages
    this is called from __init__.py
    """

    cursor = connection.cursor()
    sql = """
        INSERT INTO public.oauth2_provider_application(
            id,client_id, redirect_uris, client_type, authorization_grant_type,
            client_secret,
            name, user_id, skip_authorization, created, updated)
        VALUES (
            44,'{oauth_client_id}', 'http://localhost:8000/test', 'public', 'client-credentials',
            '{oauth_client_secret}',
            'TEST APP', {user_id}, false, '1-1-2000', '1-1-2000');
    """

    sql = sql.format(user_id=1, oauth_client_id=OAUTH_CLIENT_ID, oauth_client_secret=OAUTH_CLIENT_SECRET)
    cursor.execute(sql)


def tearDownTestPackage():
    """
    see https://nose.readthedocs.io/en/latest/writing_tests.html#test-packages
    this is called from __init__.py
    """

    se = SearchEngineFactory().create()
    se.delete_index(index="terms,concepts")
    se.delete_index(index="resources")
    se.delete_index(index="resource_relations")


def setUpModule():
    # This doesn't appear to be called because ArchesTestCase is never called directly
    # See setUpTestPackage above
    pass


def tearDownModule():
    # This doesn't appear to be called because ArchesTestCase is never called directly
    # See tearDownTestPackage above
    pass


class WardenTestCase(TestCase):
    def __init__(self, *args, **kwargs):
        super(WardenTestCase, self).__init__(*args, **kwargs)
        if settings.DEFAULT_BOUNDS is None:
            management.call_command("migrate")
            with open(os.path.join("tests/fixtures/system_settings/Arches_System_Settings_Model.json"), "r") as f:
                archesfile = JSONDeserializer().deserialize(f)
            ResourceGraphImporter(archesfile["graph"], True)
            BusinessDataImporter("tests/fixtures/system_settings/System_Settings_.json").import_business_data()
            settings.update_from_db()

    @classmethod
    def loadOntology(cls):
        ontologies_count = Ontology.objects.exclude(ontologyid__isnull=True).count()
        if ontologies_count == 0:
            management.call_command("load_ontology", source=test_settings.ONTOLOGY_PATH)

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    @classmethod
    def deleteGraph(cls, root):
        graph = Graph.objects.get(graphid=str(root))
        graph.delete()

    def setUp(self):
        pass

    def tearDown(self):
        pass


class TestSearchEngine(SearchEngine):
    def __init__(self, **kwargs):
        super(TestSearchEngine, self).__init__(**kwargs)

    def delete(self, **kwargs):
        """
        Deletes a document from the index
        Pass an index and id to delete a specific document
        Pass a body with a query dsl to delete by query

        """

        # kwargs = self.reset_index(**kwargs)
        return super(TestSearchEngine, self).delete(**kwargs)

    def delete_index(self, **kwargs):
        """
        Deletes an entire index

        """

        # kwargs = self.reset_index(**kwargs)
        return super(TestSearchEngine, self).delete_index(**kwargs)

    def search(self, **kwargs):
        """
        Search for an item in the index.
        Pass an index and id to get a specific document
        Pass a body with a query dsl to perform a search

        """

        # kwargs = self.reset_index(**kwargs)
        return super(TestSearchEngine, self).search(**kwargs)

    def create_index(self, **kwargs):
        # kwargs = self.reset_index(**kwargs)
        return super(TestSearchEngine, self).create_index(**kwargs)

    def index_data(self, index=None, body=None, idfield=None, id=None, **kwargs):
        """
        Indexes a document or list of documents into Elasticsearch

        If "id" is supplied then will use that as the id of the document

        If "idfield" is supplied then will try to find that property in the
            document itself and use the value found for the id of the document

        """

        kwargs["index"] = index
        kwargs["body"] = body
        kwargs["idfield"] = idfield
        kwargs["id"] = id
        # kwargs = self.reset_index(**kwargs)
        return super(TestSearchEngine, self).index_data(**kwargs)

    def bulk_index(self, data, **kwargs):
        kwargs["data"] = data
        # kwargs = self.reset_index(**kwargs)
        return super(TestSearchEngine, self).bulk_index(**kwargs)

    def create_bulk_item(self, **kwargs):
        # kwargs = self.reset_index(**kwargs)
        return super(TestSearchEngine, self).create_bulk_item(**kwargs)

    def count(self, **kwargs):
        # kwargs = self.reset_index(**kwargs)
        return super(TestSearchEngine, self).count(**kwargs)
