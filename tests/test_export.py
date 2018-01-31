import os.path

from kallysto.publication import Publication
from kallysto.export import Export, Value, Table, Figure
import pytest
import pandas as pd
import matplotlib.pylab as plt
import matplotlib.figure as figure
from os.path import isfile


import numpy as np

# -- Test Fixtures ------------------------------------------------------------


@pytest.fixture(scope="module")
def pub_path():
    return 'tests/sandbox/pub/'


@pytest.fixture(scope="module")
def draft(pub_path):
    return Publication(notebook='draft_nb',
                       title='draft_report',
                       root_path=pub_path)


@pytest.fixture(scope="module")
def final(pub_path):
    return Publication(notebook='final_nb',
                       title='final_report',
                       root_path=pub_path)


@pytest.fixture(scope="module")
def value1():
    return Value(name='v1', value=1)


@pytest.fixture(scope="module")
def string1():
    return Value(name='s1', value="string 1")


@pytest.fixture(scope="module")
def df():
    return pd.DataFrame([(1, 100), (2, 120), (3, 110), (4, 200)],
                        columns=['Qtr', 'Sales'])


@pytest.fixture(scope="module")
def table1(df):

    return Export.table('t1', df, caption="caption 1")


@pytest.fixture(scope="module")
def figure1(df):
    return Export.figure('f1',
                         image=df.plot().get_figure(),
                         data=df,
                         caption='caption 1')


# -- Test Basic Exports ------------------------------------------------------------


def test_value1(value1):
    assert type(value1) == Value
    assert value1.name == 'v1'
    assert value1.value == 1


def test_string1(string1):
    assert type(string1) == Value
    assert string1.name == 's1'
    assert string1.value == "string 1"


def test_table1(table1, df):

    assert type(table1) == Table
    assert table1.name == "t1"
    assert table1.caption == "caption 1"
    assert table1.data.equals(df) is True
    assert table1.data_file == "t1.csv"


def test_figure1(figure1, df):

    assert type(figure1) == Figure
    assert figure1.name == 'f1'
    assert figure1.data.equals(df) is True
    assert figure1.caption == 'caption 1'
    assert type(figure1.image) == figure.Figure


def test_value1_export_to_draft(draft, value1, pub_path):
    value1 > draft


#
# def test_value1_export_to_pub1(pub1, value1):
#     value1 > pub1
#
#     assert os.path.isfile(pub1.defs_file) is True
