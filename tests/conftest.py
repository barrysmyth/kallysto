""" PyTest Fixtures.

A bunch of fixtures that setup publications for use in testing.
"""

import pytest
from shutil import rmtree

import pandas as pd
from matplotlib.pylab import plt
    
from kallysto.publication import Publication
from kallysto.export import Export, Value, Table, Figure


@pytest.fixture(scope="module")
def pub_with_defs():
    pub = Publication(
            notebook='nb', 
            title='pub_with_defs', 
            pub_root='./tests/pub/', 
            overwrite=True, fresh_start=True, write_defs=True)
    
    yield pub
    
    # Teardown the title
    rmtree(pub.pub_root + '/' + pub.title)

@pytest.fixture(scope="module")
def pub_no_defs():
    pub = Publication(
            notebook='nb', 
            title='pub_no_defs', 
            pub_root='./tests/pub/', 
            overwrite=True, fresh_start=True, write_defs=False)
    
    yield pub
    
    # Teardown the title
    rmtree(pub.pub_root + '/' + pub.title)
    
# To make it easier to test the contents of definitions files we 
# create a number of publications as fixtures so that each one
# will be used for just one export. This ensures that their
# defintions files contain just a single defintion.

@pytest.fixture(scope="module")
def pub_for_numeric_value():
    pub = Publication(
            notebook='nb', 
            title='pub_for_numeric_value', 
            pub_root='./tests/pub/', 
            overwrite=True, fresh_start=True, write_defs=True)
    
    yield pub
    
    # Teardown the title
    rmtree(pub.pub_root + '/' + pub.title)
    

@pytest.fixture(scope="module")
def markdown_pub_for_numeric_value():
    pub = Publication(
            notebook='nb', 
            title='markdown_pub_for_numeric_value', 
            pub_root='./tests/pub/',
            formatter='markdown',
            overwrite=True, fresh_start=True, write_defs=True)
    
    yield pub
    
    # Teardown the title
    rmtree(pub.pub_root + '/' + pub.title)

@pytest.fixture(scope="module")
def pub_for_string_value():
    pub = Publication(
            notebook='nb', 
            title='pub_for_string_value', 
            pub_root='./tests/pub/', 
            overwrite=True, fresh_start=True, write_defs=True)
    
    yield pub
    
    # Teardown the title
    rmtree(pub.pub_root + '/' + pub.title)

@pytest.fixture(scope="module")
def pub_for_table():
    pub = Publication(
            notebook='nb', 
            title='pub_for_table', 
            pub_root='./tests/pub/', 
            overwrite=True, fresh_start=True, write_defs=True)
    
    yield pub
    
    # Teardown the title
    rmtree(pub.pub_root + '/' + pub.title)

@pytest.fixture(scope="module")
def pub_for_figure():
    pub = Publication(
            notebook='nb', 
            title='pub_for_figure', 
            pub_root='./tests/pub/', 
            overwrite=True, fresh_start=True, write_defs=True)
    
    yield pub
    
    # Teardown the title
    rmtree(pub.pub_root + '/' + pub.title)


@pytest.fixture(scope="module")
def numeric_value():
    return Export.value('NumericValue', 1)
    
@pytest.fixture(scope="module")
def string_value():
    return Export.value('StringValue', "string")


@pytest.fixture(scope="module")
def df():
    return pd.DataFrame([[1, 2, 3], [4, 5, 6]], columns=['a', 'b', 'c'], index=['x', 'y'])

@pytest.fixture(scope="module")
def table(df):
    return Export.table(
        "Table",
        data=df,
        caption="A table caption."
    )


@pytest.fixture(scope="module")
def figure(df):
    
    fig, ax = plt.subplots(figsize=(12, 4))
    df.plot(ax=ax)

    return Export.figure(
        "Figure",
        image=fig,
        data=df,
        caption="A figure caption."
    )

@pytest.fixture(scope="module")
def pub_using_markdown():
    pub = Publication(
            notebook='nb', 
            title='pub_using_markdown', 
            pub_root='./tests/pub/',
            formatter='markdown',
            overwrite=True, fresh_start=True, write_defs=True)
    
    yield pub
    
    # Teardown the title
    rmtree(pub.pub_root + '/' + pub.title)