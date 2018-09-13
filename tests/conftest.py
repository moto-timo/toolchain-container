import pytest

def pytest_addoption(parser):
    parser.addoption("--testimage", action="store",
                     help="image to test")

@pytest.fixture
def testimage(request):
    return request.config.getoption("--testimage")
