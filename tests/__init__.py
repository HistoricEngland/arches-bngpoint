def setup_package():
    from .base_test import setUpTestPackage
    print("tests.__init__.setupPackage")
    setUpTestPackage()


def teardown_package():
    from .base_test import tearDownTestPackage
    print("tests.__init__.tearDonwPackage")
    tearDownTestPackage()
