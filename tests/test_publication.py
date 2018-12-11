import os
import pytest

from kallysto.publication import Publication

def test_publication_is_a_publication(pub_with_defs):
    assert type(pub_with_defs) == Publication
    
def test_publication_data_store(pub_with_defs): 
    """Check for the main data store directories and files."""
    
    # Check the title directory exists
    assert os.path.isdir(pub_with_defs.pub_path) is True
    
    # Check each of the main data store dirs exist.
    for name in ['data', 'figs', 'defs', 'logs']:
        dir_path = getattr(pub_with_defs, '{}_path'.format(name))
        assert os.path.isdir(dir_path) is True
        
    # Check the src dir exists
    assert os.path.isdir(pub_with_defs.src_path) is True
        
    # Check the log file exists.
    logs_file = pub_with_defs.logs_file
    assert os.path.isfile(logs_file) is True
    
def test_write_defs(pub_with_defs, pub_no_defs):
    """Test the write_defs behavior.
    
    Make sure that a _definitions.tex is created when write_defs
    is True and that there is no file created when write_defs is False."""
    
    assert pub_with_defs.write_defs is True
    
    with_defs_file = pub_with_defs.defs_file
    
    assert os.path.isfile(with_defs_file) is True


    assert pub_no_defs.write_defs is False
    
    no_defs_file = pub_no_defs.defs_file
    assert os.path.isfile(no_defs_file) is False
    
    
def test_markdown_publication_data_store(pub_using_markdown): 
    """Check for the main data store directories and files."""
    
    # Check the title directory exists
    assert os.path.isdir(pub_using_markdown.pub_path) is True
    
    # Check each of the main data store dirs exist.
    for name in ['data', 'figs', 'defs', 'logs']:
        dir_path = getattr(pub_using_markdown, '{}_path'.format(name))
        assert os.path.isdir(dir_path) is True
        
    # Check the src dir exists
    assert os.path.isdir(pub_using_markdown.src_path) is True
    
    # Check the log file exists.
    logs_file = pub_using_markdown.logs_file
    assert os.path.isfile(logs_file) is True
    
def test_value_def_meta_data_for_nb(pub_using_markdown, numeric_value):
    """Check that the nb is reachable based on the def meta-data."""
    
    # Export a value to the markdown publication.
    numeric_value > pub_using_markdown
    
    # The path to the nb used in the meta data of the definition.
    meta_data_nb_path = numeric_value.path_to(
        pub_using_markdown.src_path, pub_using_markdown.notebook_file)
    
    # Check the meta data nb path is accessible from the src dir.
    cwd = os.getcwd()  # CWD is the nb for this test.
    os.chdir(pub_using_markdown.src_path)  # Switch to the src dir.
    os.chdir(os.path.split(meta_data_nb_path)[0])  # Switch to the dir of the nb
    
    assert os.getcwd() == cwd  # Confirm same as original cwd
    
    os.chdir(cwd)  # Change back to the tests dir.
    
    
def test_value_def_meta_data_for_data_file(pub_using_markdown, numeric_value):
    """Check that the data_file is reachable based on the def meta-data."""

    # Export a value to the markdown publication.
    numeric_value > pub_using_markdown
    
    # The path to the value data file.
    meta_data_data_file = numeric_value.path_to(
        pub_using_markdown.src_path, 
        pub_using_markdown.data_file(numeric_value.data_file))
    
    # Check the meta data nb path is accessible from the src dir.
    cwd = os.getcwd()  # CWD is the nb for this test.
    os.chdir(pub_using_markdown.src_path)  # Switch to the src dir.
    
    assert os.path.isfile(meta_data_data_file)
    
    os.chdir(cwd)  # Change back to the tests dir.
    
    
def test_table_def_meta_data_for_nb(pub_using_markdown, table):
    """Check that the nb is reachable based on the def meta-data."""
    
    # Export a value to the markdown publication.
    table > pub_using_markdown
    
    # The path to the nb used in the meta data of the definition.
    meta_data_nb_path = table.path_to(
        pub_using_markdown.src_path, pub_using_markdown.notebook_file)
    
    # Check the meta data nb path is accessible from the src dir.
    cwd = os.getcwd()  # CWD is the nb for this test.
    os.chdir(pub_using_markdown.src_path)  # Switch to the src dir.
    os.chdir(os.path.split(meta_data_nb_path)[0])  # Switch to the dir of the nb
    
    assert os.getcwd() == cwd  # Confirm same as original cwd
    
    os.chdir(cwd)  # Change back to the tests dir.
    
    
def test_table_def_meta_data_for_data_file(pub_using_markdown, table):
    """Check that the data_file is reachable based on the def meta-data."""

    # Export a value to the markdown publication.
    table > pub_using_markdown
    
    # The path to the value data file.
    meta_data_data_file = table.path_to(
        pub_using_markdown.src_path, 
        pub_using_markdown.data_file(table.data_file))
    
    # Check the meta data nb path is accessible from the src dir.
    cwd = os.getcwd()  # CWD is the nb for this test.
    os.chdir(pub_using_markdown.src_path)  # Switch to the src dir.
    
    assert os.path.isfile(meta_data_data_file)
    
    os.chdir(cwd)  # Change back to the tests dir.
    
    
def test_figure_def_meta_data_for_nb(pub_using_markdown, figure):
    """Check that the nb is reachable based on the def meta-data."""
    
    # Export a value to the markdown publication.
    figure > pub_using_markdown
    
    # The path to the nb used in the meta data of the definition.
    meta_data_nb_path = figure.path_to(
        pub_using_markdown.src_path, pub_using_markdown.notebook_file)
    
    # Check the meta data nb path is accessible from the src dir.
    cwd = os.getcwd()  # CWD is the nb for this test.
    os.chdir(pub_using_markdown.src_path)  # Switch to the src dir.
    os.chdir(os.path.split(meta_data_nb_path)[0])  # Switch to the dir of the nb
    
    assert os.getcwd() == cwd  # Confirm same as original cwd
    
    os.chdir(cwd)  # Change back to the tests dir.
    
    
def test_figure_def_meta_data_for_data_file(pub_using_markdown, figure):
    """Check that the data_file is reachable based on the def meta-data."""

    # Export a value to the markdown publication.
    figure > pub_using_markdown
    
    # The path to the value data file.
    meta_data_data_file = figure.path_to(
        pub_using_markdown.src_path, 
        pub_using_markdown.data_file(figure.data_file))
    
    # Check the meta data nb path is accessible from the src dir.
    cwd = os.getcwd()  # CWD is the nb for this test.
    os.chdir(pub_using_markdown.src_path)  # Switch to the src dir.
    
    assert os.path.isfile(meta_data_data_file)  # Confirm same as original cwd
    
    os.chdir(cwd)  # Change back to the tests dir.
    
    
def test_figure_def_meta_data_for_image_file(pub_using_markdown, figure):
    """Check that the image file is reachable based on the def meta-data."""

    # Export a value to the markdown publication.
    figure > pub_using_markdown
    
    # The path to the value data file.
    meta_data_image_file = figure.path_to(
        pub_using_markdown.src_path, 
        pub_using_markdown.fig_file(figure.image_file))
    
    # Check the meta data nb path is accessible from the src dir.
    cwd = os.getcwd()  # CWD is the nb for this test.
    os.chdir(pub_using_markdown.src_path)  # Switch to the src dir.
    
    assert os.path.isfile(meta_data_image_file)
    
    os.chdir(cwd)  # Change back to the tests dir.


def test_value_log_for_nb(pub_using_markdown, numeric_value):
    """Check that the nb is reachable based on the log data."""
    
    # Export a value to the markdown publication.
    numeric_value > pub_using_markdown
    
    # The path to the nb used in the log.
    log_nb_path = numeric_value.path_to(pub_using_markdown.logs_path, pub_using_markdown.notebook_file)
    
    # Check the nb path is accessible from the log.
    cwd = os.getcwd()  # CWD is the nb for this test.
    os.chdir(pub_using_markdown.logs_path)  # Switch to the logs dir.
    os.chdir(os.path.split(log_nb_path)[0])  # Switch to the dir of the nb
    
    assert os.getcwd() == cwd  # Confirm same as original cwd
    
    os.chdir(cwd)  # Change back to the tests dir.
    

def test_value_log_for_data_file(pub_using_markdown, numeric_value):
    """Check that the nb is reachable based on the log data."""
    
    # Export a value to the markdown publication.
    numeric_value > pub_using_markdown
    
    # The path to the nb used in the log.
    log_data_file = numeric_value.path_to(
        pub_using_markdown.logs_path, 
        pub_using_markdown.data_file(numeric_value.data_file))
        
    # Check the data file path is accessible from the log dir.
    cwd = os.getcwd()  
    
    os.chdir(pub_using_markdown.logs_path)  # Switch to the logs dir.
    assert os.path.isfile(log_data_file)    # Check the data file exists from here.
    
    os.chdir(cwd)  # Change back to the tests dir.


def test_table_log_for_nb(pub_using_markdown, table):
    """Check that the nb is reachable based on the log data."""
    
    # Export a value to the markdown publication.
    table > pub_using_markdown
    
    # The path to the nb used in the log.
    log_nb_path = table.path_to(pub_using_markdown.logs_path, pub_using_markdown.notebook_file)
    
    # Check the nb path is accessible from the log.
    cwd = os.getcwd()  # CWD is the nb for this test.
    os.chdir(pub_using_markdown.logs_path)  # Switch to the logs dir.
    os.chdir(os.path.split(log_nb_path)[0])  # Switch to the dir of the nb
    
    assert os.getcwd() == cwd  # Confirm same as original cwd
    
    os.chdir(cwd)  # Change back to the tests dir.
    

def test_table_log_for_data_file(pub_using_markdown, table):
    """Check that the nb is reachable based on the log data."""
    
    # Export a value to the markdown publication.
    table > pub_using_markdown
    
    # The path to the nb used in the log.
    log_data_file = table.path_to(
        pub_using_markdown.logs_path, 
        pub_using_markdown.data_file(table.data_file))
        
    # Check the data file path is accessible from the log dir.
    cwd = os.getcwd()  
    
    os.chdir(pub_using_markdown.logs_path)  # Switch to the logs dir.
    assert os.path.isfile(log_data_file)    # Check the data file exists from here.
    
    os.chdir(cwd)  # Change back to the tests dir.


def test_figure_log_for_nb(pub_using_markdown, figure):
    """Check that the nb is reachable based on the log data."""
    
    # Export a value to the markdown publication.
    figure > pub_using_markdown
    
    # The path to the nb used in the log.
    log_nb_path = figure.path_to(pub_using_markdown.logs_path, pub_using_markdown.notebook_file)
    
    # Check the nb path is accessible from the log.
    cwd = os.getcwd()  # CWD is the nb for this test.
    os.chdir(pub_using_markdown.logs_path)  # Switch to the logs dir.
    os.chdir(os.path.split(log_nb_path)[0])  # Switch to the dir of the nb
    
    assert os.getcwd() == cwd  # Confirm same as original cwd
    
    os.chdir(cwd)  # Change back to the tests dir.
    

def test_figure_log_for_data_file(pub_using_markdown, figure):
    """Check that the nb is reachable based on the log data."""
    
    # Export a value to the markdown publication.
    figure > pub_using_markdown
    
    # The path to the nb used in the log.
    log_data_file = figure.path_to(
        pub_using_markdown.logs_path, 
        pub_using_markdown.data_file(figure.data_file))
        
    # Check the data file path is accessible from the log dir.
    cwd = os.getcwd()  
    
    os.chdir(pub_using_markdown.logs_path)  # Switch to the logs dir.
    assert os.path.isfile(log_data_file)    # Check the data file exists from here.
    
    os.chdir(cwd)  # Change back to the tests dir.


def test_figure_log_for_image_file(pub_using_markdown, figure):
    """Check that the nb is reachable based on the log data."""
    
    # Export a value to the markdown publication.
    figure > pub_using_markdown
    
    # The path to the nb used in the log.
    log_image_file = figure.path_to(
        pub_using_markdown.logs_path, 
        pub_using_markdown.fig_file(figure.image_file))
        
    # Check the data file path is accessible from the log dir.
    cwd = os.getcwd()  
    
    os.chdir(pub_using_markdown.logs_path)  # Switch to the logs dir.
    assert os.path.isfile(log_image_file)    # Check the data file exists from here.
    
    os.chdir(cwd)  # Change back to the tests dir.



