import os.path

from kallysto.publication import Publication
import pytest

# Test fixtures to setup bridge.


@pytest.fixture(scope="module")
def config1():
    return {'notebook': 'nb1',
            'title': 'pub1',
            'root_path': 'tests/sandbox/pub/'}


@pytest.fixture(scope="module")
def config2():
    return {'notebook': 'nb2',
            'title': 'pub2',
            'root_path': 'tests/sandbox/pub/'}


def check_init_publication(config):
    pub1 = Publication(**config)

    assert type(pub1) == Publication

    # Check that the root_path exists.
    assert os.path.isdir(pub1.root_path) is True

    # Check for the standard kallysto dirs.
    assert os.path.isdir(pub1.figs_path) is True
    assert os.path.isdir(pub1.data_path) is True
    assert os.path.isdir(pub1.defs_path) is True

    # Check for the standard kallysto defs and logs files.
    assert os.path.isfile(pub1.defs_file) is True
    assert os.path.isfile(pub1.logs_file) is True


def test_init_publication_with_config1(config1):
    check_init_publication(config1)


def test_init_publication_with_config2(config2):
    check_init_publication(config2)


def test_delete_publication_with_config1(config1):
    pub1 = Publication(**config1)

    pub1.delete()
    assert os.path.isdir(pub1.figs_path) is False
    assert os.path.isdir(pub1.data_path) is False
    assert os.path.isdir(pub1.defs_path) is False

    # Check for the standard kallysto defs and logs files.
    assert os.path.isfile(pub1.defs_file) is False
    assert os.path.isfile(pub1.logs_file) is False
