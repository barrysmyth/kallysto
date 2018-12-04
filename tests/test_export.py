import os
import pytest
import pandas as pd
from matplotlib.pylab import plt
from matplotlib.figure import Figure as Fig

from kallysto.publication import Publication
from kallysto.export import Export, Value, Table, Figure


    
# Test the export objects.
def test_numeric_value(numeric_value):
    assert type(numeric_value) == Value
    assert numeric_value.name == 'NumericValue'
    assert numeric_value.value == 1
    
def test_string_value(string_value):
    assert string_value.name == 'StringValue'
    assert string_value.value == "string"
    
def test_table(table, df):
    assert type(table) == Table
    assert table.name == 'Table'
    assert table.data.equals(df) is True
    assert table.caption == "A table caption."
    
def test_figure(figure, df):
    assert type(figure) == Figure
    assert type(figure.image) == Fig
    assert figure.name == 'Figure'
    assert figure.data.equals(df) is True
    assert figure.caption == "A figure caption."

    
# Test the transfers for each of the export.

def test_numeric_value_export(numeric_value, pub_for_numeric_value):
    
    numeric_value > pub_for_numeric_value
    
    value_file = pub_for_numeric_value.kallysto_path+pub_for_numeric_value.data_file(
        numeric_value.data_file)
    
    # Test the file exists.
    assert os.path.isfile(value_file)

    # Test the contents match the value data.
    with open(value_file,"r") as vf:
        assert str(numeric_value.value) == vf.read()


def test_string_value_export(string_value, pub_for_string_value):
    
    string_value > pub_for_string_value
    
    value_file = pub_for_string_value.kallysto_path+pub_for_string_value.data_file(
        string_value.data_file)
    
    
    # Test the file exists.
    assert os.path.isfile(value_file)

    # Test the contents match the value data.
    with open(value_file,"r") as vf:
        assert string_value.value == vf.read()
        

def test_table_export(table, pub_for_table):
    
    table > pub_for_table
    
    data_file = pub_for_table.kallysto_path+pub_for_table.data_file(table.data_file)
    
    
    # Test the file exists.
    assert os.path.isfile(data_file)

    # Test the contents match the table data; the first col is the index.
    df = pd.read_csv(data_file, index_col=0)
    assert table.data.equals(df)

    # Generate a table defintion string based on the formatted for pub_for_table.
    table_def = ''.join(pub_for_table.formatter.table(table, pub_for_table).split('\n')[6:])
                
    # Read in the defintion from the definitions file of pub_for_table
    # and compare to the newly generated defintion string; exclude the
    # meta data, which contains id and timing information.
    defs_file = pub_for_table.kallysto_path+pub_for_table.defs_file
    with open(defs_file,"r") as df:
        table_def_from_file = ''.join(df.read().split('\n')[6:])
        assert table_def == table_def_from_file
        
    
def test_figure_export(figure, pub_for_figure):
    
    figure > pub_for_figure
    
    data_file = pub_for_figure.kallysto_path+pub_for_figure.data_file(figure.data_file)
    
    # Test the file exists.
    assert os.path.isfile(data_file)

    # Test the contents match the table data; the first col is the index.
    df = pd.read_csv(data_file, index_col=0)
    assert figure.data.equals(df)

    # Since the images are exported as PDFs, it's messy to test.
    # Instead, check that image file exists.
    image_file = pub_for_figure.kallysto_path+pub_for_figure.fig_file(figure.image_file)
    assert os.path.isfile(image_file) is True
    
    # Generate a table defintion string based on the formatted for pub_for_figure.
    figure_def = ''.join(pub_for_figure.formatter.figure(figure, pub_for_figure).split('\n')[6:])
                
    # Read in the defintion from the definitions file of pub_for_figure
    # and compare to the newly generated defintion string; exclude the
    # meta data, which contains id and timing information.
    defs_file = pub_for_figure.kallysto_path+pub_for_figure.defs_file
    with open(defs_file,"r") as df:
        figure_def_from_file = ''.join(df.read().split('\n')[6:])
        assert figure_def == figure_def_from_file
        
        

def test_numeric_value_export_to_markdown(numeric_value, markdown_pub_for_numeric_value):
    
    numeric_value > markdown_pub_for_numeric_value
    
    value_file = markdown_pub_for_numeric_value.kallysto_path+\
        markdown_pub_for_numeric_value.data_file(numeric_value.data_file)
    
    # Test the file exists.
    assert os.path.isfile(value_file)

    # Test the contents match the value data.
    with open(value_file,"r") as vf:
        assert str(numeric_value.value) == vf.read()