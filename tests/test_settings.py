import os, platform
import inspect
from warden.settings import *

try:
    from warden.settings_local import *
except ImportError:
    pass

if platform.system().lower() != "windows":
    del GDAL_LIBRARY_PATH

PACKAGE_NAME = "warden"
INIT_ROOT = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
#ROOT_DIR = 
TEST_ROOT = os.path.normpath(os.path.join(INIT_ROOT, "..", "tests"))
ROOT_DIR = os.path.normpath(os.path.join(ROOT_DIR, "..", "..", "arches", "arches")) #<< don't change to 'warden'!

ONTOLOGY_FIXTURES = os.path.join(TEST_ROOT, "fixtures", "ontologies", "test_ontology")
ONTOLOGY_PATH = os.path.join(TEST_ROOT, "fixtures", "ontologies", "cidoc_crm")

SEARCH_BACKEND = "tests.base_test.TestSearchEngine"

RESOURCE_GRAPH_LOCATIONS = (os.path.join(TEST_ROOT, "fixtures", "resource_graphs"),)

MAPBOX_API_KEY = "pk.eyJ1IjoiaGlzdG9yaWN1bmNsZSIsImEiOiJja2MwbnIyZ28xbGV4Mnd0Yms1cTh3YnFyIn0.SgiBtpnnmb6ElvfRTlLbMQ"

BUSISNESS_DATA_FILES = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

ELASTICSEARCH_PREFIX = "test"



# could add Chrome, PhantomJS etc... here
LOCAL_BROWSERS = []  # ['Firefox']

RUN_LOCAL = True

OVERRIDE_RESOURCE_MODEL_LOCK = True

# Use nose to run all tests
TEST_RUNNER = "django_nose.NoseTestSuiteRunner"

# Tell nose to measure coverage on the 'foo' and 'bar' apps
NOSE_ARGS = [
    "--with-coverage", 
    "--nologcapture", 
    "--cover-package=warden",
    "--cover-erase",
    #'--with-xunit',
    #'--xunit-file=tests/results/xunit-results.xml',
    '--verbosity=2',
    #'--cover-html',
    #'--cover-html-dir=tests/results/coverage-report',
    ]


INSTALLED_APPS = INSTALLED_APPS + ("django_nose",)

WARDEN_WIDGETS_LOCATION = os.path.normpath(os.path.join(INIT_ROOT, "..", "warden", "widgets"))
WARDEN_DATATYPES_LOCATION = os.path.normpath(os.path.join(INIT_ROOT, "..", "warden", "datatypes"))
WARDEN_FUNCTIONS_LOCATION = os.path.normpath(os.path.join(INIT_ROOT, "..", "warden", "functions"))

