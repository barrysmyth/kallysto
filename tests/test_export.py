import os.path

from kallysto.publication import Publication
from kallysto.export import Export, Value, Table, Figure
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


@pytest.fixture(scope="module")
def value1():
    return Value(name='v1', value=1)


@pytest.fixture(scope="module")
def pub1():
    return Publication(notebook='nb1',
                       title='pub1',
                       root_path='tests/sandbox/pub/')


def test_value1():
    v = Value(name='v1', value=1)
    assert type(v) == Value
    assert v.name == 'v1'
    assert v.value == 1
    assert v1.name == 'v1'
    assert v1.value == 1


def test_value1_export_to_pub1(pub1, value1):
    value1 > pub1

    assert os.path.isfile(pub1.defs_file) is True
