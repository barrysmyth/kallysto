import os.path
from shutil import rmtree
from kallysto.publication import Publication
import pytest

# -- Test Fixtures ------------------------------------------------------------


@pytest.fixture(scope="module")
def interim_config():
    return {'notebook': 'interim_nb',
            'title': 'interim_report',
            'root_path': 'tests/sandbox/testpub/'}


@pytest.fixture(scope="module")
def final_config():
    return {'notebook': 'final_nb',
            'title': 'final_report',
            'root_path': 'tests/sandbox/testpub/'}


@pytest.fixture(scope="module")
def interim_config_without_defs():
    return {'notebook': 'interim_nb',
            'title': 'interim_report',
            'root_path': 'tests/sandbox/testpub/',
            'write_defs': False}


@pytest.fixture(scope="module")
def final_config_without_defs():
    return {'notebook': 'final_nb',
            'title': 'final_report',
            'root_path': 'tests/sandbox/testpub/',
            'write_defs': False}


@pytest.fixture(scope="module")
def interim_config_with_defs():
    return {'notebook': 'interim_nb',
            'title': 'interim_report',
            'root_path': 'tests/sandbox/testpub/',
            'write_defs': True}


@pytest.fixture(scope="module")
def final_config_with_defs():
    return {'notebook': 'final_nb',
            'title': 'final_report',
            'root_path': 'tests/sandbox/testpub/',
            'write_defs': True}


def check_publication_dirs(config):

    rmtree(config['root_path'])  # Start with a blank state.

    pub = Publication(**config)

    assert type(pub) == Publication

    # Check that the root_path exists.
    assert os.path.isdir(pub.root_path)

    # Check for the standard kallysto dirs.
    assert os.path.isdir(pub.figs_path)
    assert os.path.isdir(pub.data_path)
    assert os.path.isdir(pub.logs_path)

    # Check the defs_file.
    if not('write_defs' in config):
        assert os.path.isdir(pub.defs_path)
        assert os.path.isfile(pub.defs_file)
    elif config['write_defs']:
        assert os.path.isdir(pub.defs_path)
        assert os.path.isfile(pub.defs_file)
    else:
        assert os.path.isdir(pub.defs_path) is False
        assert os.path.isfile(pub.defs_file) is False

    # Check the logs file.
    assert os.path.isfile(pub.logs_file)


def test_interim_pub(interim_config):
    check_publication_dirs(interim_config)


def test_final_pub(final_config):
    check_publication_dirs(final_config)


def test_interim_pub_with_defs(interim_config_without_defs):
    check_publication_dirs(interim_config_without_defs)


def test_final_pub_with_defs(final_config_without_defs):
    check_publication_dirs(final_config_without_defs)


def test_interim_pub_without_defs(interim_config_without_defs):
    check_publication_dirs(interim_config_without_defs)


def test_final_pub_without_defs(final_config_without_defs):
    check_publication_dirs(final_config_without_defs)
