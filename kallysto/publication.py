# -*- coding: utf-8 -*-

# $$\                $$\ $$\                       $$\
# $$ |               $$ |$$ |                      $$ |
# $$ |  $$\ $$$$$$\  $$ |$$ |$$\   $$\  $$$$$$$\ $$$$$$\    $$$$$$\
# $$ | $$  |\____$$\ $$ |$$ |$$ |  $$ |$$  _____|\_$$  _|  $$  __$$\
# $$$$$$  / $$$$$$$ |$$ |$$ |$$ |  $$ |\$$$$$$\    $$ |    $$ /  $$ |
# $$  _$$< $$  __$$ |$$ |$$ |$$ |  $$ | \____$$\   $$ |$$\ $$ |  $$ |
# $$ | \$$\\$$$$$$$ |$$ |$$ |\$$$$$$$ |$$$$$$$  |  \$$$$  |\$$$$$$  |
# \__|  \__|\_______|\__|\__| \____$$ |\_______/    \____/  \______/
#                            $$\   $$ |
#                            \$$$$$$  |
#                             \______/
#
# Copyright 2017 Barry Smnyth
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice & this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
Create a  publication linking a notebook to a publication title.

Creates a set of subfolders within a publication title folder inside
the publication root of the project. The location of this publication
root, relative to a notebook, and the names of the created
subfolders can be configured through the constructor.

Also includes configurations for whether or not to overwrite existing
folders/files/logs as well as whether to create seperate definition files,
and when definition files are to be created, which formatter to use.

Example Usage:

The following doctests check the basic publication setup by creating two
publication targets.

>>> from kallysto.publication import Publication

# Create a new publication as an export target (interim_report). It is assumed
# this code is run in a notebook (notebook_0) and that the interim_report is
# located at 'tests/sandbox/' relative to the notebook.
>>> interim = Publication('notebook_0', 'interim_report', write_defs=False, \
root_path='tests/sandbox/', overwrite=True, delete_log=True)

# Create another publication as an export target (final_report). It is assumed
# this code is run in a notebook (notebook_1) and that the final_report is
# located at 'tests/sandbox/' relative to the notebook.
>>> final = Publication('notebook_1', 'final_report', \
root_path='tests/sandbox/', overwrite=True, delete_log=True)

>>> interim
Publication(notebook_0, interim_report, formatter=<class \
'kallysto.formatter.Latex'>, write_defs=False, overwrite=True, \
delete_log=True, root_path=tests/sandbox/, main_path=../../, figs_dir=figs/, \
defs_dir=defs/, data_dir=data/, logs_dir=logs/, \
definitions_file=tests/sandbox/interim_report/defs/notebook_0/_definitions.tex,\
 logs_file='_kallysto.log')
>>> final
Publication(notebook_1, final_report, formatter=<class \
'kallysto.formatter.Latex'>, write_defs=True, overwrite=True, \
delete_log=True, root_path=tests/sandbox/, main_path=../../, figs_dir=figs/, \
defs_dir=defs/, data_dir=data/, logs_dir=logs/, \
definitions_file=tests/sandbox/final_report/defs/notebook_1/_definitions.tex, \
logs_file='_kallysto.log')

# Printing the publication objects shows the main target locations.
>>> print(interim)
Locations:
  tests/sandbox/interim_report/
    tests/sandbox/interim_report/defs/notebook_0/_definitions.tex
    tests/sandbox/interim_report/figs/notebook_0/
    tests/sandbox/interim_report/data/notebook_0/
    tests/sandbox/interim_report/logs/_kallysto.log
Settings:
  overwrite: True
  delete_log: True
  formatter: <class 'kallysto.formatter.Latex'>
  write_defs: False

>>> print(final)
Locations:
  tests/sandbox/final_report/
    tests/sandbox/final_report/defs/notebook_1/_definitions.tex
    tests/sandbox/final_report/figs/notebook_1/
    tests/sandbox/final_report/data/notebook_1/
    tests/sandbox/final_report/logs/_kallysto.log
Settings:
  overwrite: True
  delete_log: True
  formatter: <class 'kallysto.formatter.Latex'>
  write_defs: True
"""

# -- Publication ---------------------------------------------------------------

import logging
import os
import sys
from shutil import rmtree

from kallysto.formatter import Latex
from kallysto.export import Value, Table, Figure


class Publication():
    """Create a  publication linking a notebook to a publication title.

    Creates a set of subfolders within a publication title folder inside
    the publication root of the project. The location of this publication
    root, relative to a notebook, and the names of the created
    subfolders can be configured through the constructor.

    Also includes configurations for whether or not to overwrite existing
    folders/files/logs as well as whether to create seperate definition files,
    and when definition files are to be created, which formatter to use.

    Attributes:

        display_logger: basic logger for information and warning messages.
        audit_logger: main export logger writing to log_file.

        exports: a list of the exports
        formatter: a format class for formatting the export defintions.
        write_defs: whether or not to write a defintions file.

        overwrite: whether or not to overwrite existing publications files/dirs.
        delete_log: whether or not to delete existing log.

        title: publication title (user defined).
        notebook: source notebook name or nickname (user defined).

        root_path: relative path from source notebook to publication root.
        main_path: relative path from publication main (e.g. main.tex) to root.

        figs_dir: directory name for fig exports.
        data_dir: directory name for data exports (for tables & figures)
        defs_dir: directory name for export definitions.
        logs_dir: directory name for log.

        figs_path: path to figs_dir
        data_path: path to data_dir
        defs_path: path to defs_dir
        logs_path: path to logs_dir

        defs_file: name of definitions file.
        logs_file: name of log file.
    """

# -- Init ----------------------------------------------------------------------

    def __init__(self, notebook, title,

                 formatter=Latex,

                 write_defs=True,

                 overwrite=False, delete_log=False,

                 # Default configuration settings.
                 root_path='../../pubs/',  # From notebook to pubs root
                 main_path='../../',       # From main.tex to pubs root
                 figs_dir='figs/',
                 defs_dir='defs/',
                 data_dir='data/',
                 logs_dir='logs/',
                 defs_filename='_definitions.tex',
                 logs_filename='_kallysto.log',):
        """Constructor for a new pub, connecting a notebook to pub title.

        Args:
            notebook: the notebook in which the publication is created.
            title: the title of the publication.

            formatter: the formatter to use for creating export defintions.

            root_path: the relative path to the pub root from the notebook.
            main_path: the relative path from main pub source to pub root.

            defs_dir: the name of the defintions subfolder (e.g. defs).
            figs_dir: the name of the subfolder to hold images for figs.
            data_dir: the subfolder to hold data files for tables/figs.
            logs_dir: the name of the subfolder holding the kallysto log.

            overwrite: If true delete pub folders and files for publication.
            delete_log: If true rm log folder & file for the publication.
        """
        # A simple display logger that writes progress to screen.
        self.display_logger = logging.getLogger(
            "Kallysto:{}:{}: ".format(title, notebook))
        self.display_logger.setLevel(logging.INFO)

        self.exports = []  # To keep track of exports made thru pub.

        self.formatter = formatter

        self.write_defs = write_defs
        self.title = title
        self.notebook = notebook
        self.root_path = root_path
        self.main_path = main_path
        self.defs_dir = defs_dir
        self.logs_dir = logs_dir
        self.figs_dir = figs_dir
        self.data_dir = data_dir
        self.defs_filename = defs_filename
        self.logs_filename = logs_filename

        # Cleanup/overwrite existing publication.
        self.overwrite = overwrite
        self.delete_log = delete_log

        if self.overwrite:
            self.cleanup_notebook_files()

        # Create/setup the notebook directories.
        self.setup_notebook_directories()

        # Setup logging; defs logger and audit logger.
        self.setup_logging()

# -- @properties ---------------------------------------------------------------

    @property
    def figs_path(self):
        return "{}{}/{}{}/".format(
            self.root_path, self.title, self.figs_dir, self.notebook)

    @property
    def defs_path(self):
        return "{}{}/{}{}/".format(
            self.root_path, self.title, self.defs_dir, self.notebook)

    @property
    def data_path(self):
        return "{}{}/{}{}/".format(
            self.root_path, self.title, self.data_dir, self.notebook)

    @property
    def logs_path(self):
        return "{}{}/{}".format(
            self.root_path, self.title, self.logs_dir)

    @property
    def defs_file(self):
        return self.defs_path + self.defs_filename

    @property
    def logs_file(self):
        return self.logs_path + self.logs_filename


# -- Init Helpers --------------------------------------------------------------

    def cleanup_notebook_files(self):
        """Cleanup existing publication files if they exist.

        Delete folders and files associated with the current publication. Dont
        delete the central log unless expressly indicated by delete_log.

        Args:
            delete_log: If True, delete central log file.
        """
        self.display_logger.info(
            'Removing export files for {}:{}'.format(self.title, self.notebook))

        # If delete_log == True then delete log file.
        if self.delete_log:
            try:
                self.display_logger.info(
                    'Trying to remove {}.'.format(self.logs_file))
                os.remove(self.logs_file)
                self.display_logger.info(
                    'Removed {}.'.format(self.logs_file))

            except OSError:
                pass

        # Remove notebook definitions file, if it exists.
        try:
            self.display_logger.info(
                'Trying to remove {}.'.format(self.defs_file))
            os.remove(self.defs_file)
            self.display_logger.info(
                'Removed {}.'.format(self.defs_file))

        except OSError:
            pass

        # Prepare to remove the notebook folders for defs, figs and data.
        folders = [self.defs_path, self.figs_path, self.data_path]
        if self.delete_log:
            folders.append(self.logs_path)

        # Next, delete the folders themselves.
        for folder in folders:
            try:
                self.display_logger.info('Trying to remove {}.'.format(folder))
                rmtree(folder)
                self.display_logger.info('Removed {}.'.format(folder))

            except OSError:
                self.display_logger.info(
                    'Failed to remove {}. Probably no directory.'.format(
                        folder))
                pass

    def setup_notebook_directories(self):
        """Create the folders and files for a new publication."""

        self.display_logger.info(
            'Creating export locations for {}:{}.'.format(
                self.title, self.notebook))

        # Create main root if it doesn't exist;  top-level pubs directory.
        self.display_logger.info('Creating {}.'.format(self.root_path))
        os.makedirs(self.root_path, exist_ok=True)

        # Create the title if it doesn't exist;
        # self.pubroot = root/title/, top-level folder for this pub title.
        self.display_logger.info(
            'Creating {}{}.'.format(self.root_path, self.title))
        os.makedirs(self.root_path + self.title, exist_ok=True)

        folders = [self.figs_path, self.data_path, self.logs_path]

        # Add defs path if definitions are to be written.
        if self.write_defs:
            folders.append(self.defs_path)

        # Create main folders for defs, figs, data and logs if necessary.
        for folder in folders:
            self.display_logger.info('Creating {}.'.format(folder))
            os.makedirs(folder, exist_ok=True)

        # Create the definitions file is needed.
        if self.write_defs:
            self.display_logger.info(
                'Creating {} if it does not exist.'.format(self.defs_file))
            open(self.defs_file, 'a').close()

        # Create logs file.
        self.display_logger.info(
            'Creating {} if it does not exist.'.format(self.logs_file))
        open(self.logs_file, 'a').close()

    def setup_logging(self):
        """Setup Kallysto's logging.

        Kallysto uses three loggers: (1) A display logger to information
        messages to the screen; (2) an audit logger to log exports to a
        central log file associated with the publication; and (3) a defs
        logger for writing the export defintions.
        """

        # A file-based logger to create an kallysto audit trail.
        self.audit_logger = logging.getLogger(
            "audit_{}:{}".format(self.title, self.notebook))
        self.audit_logger.setLevel(logging.INFO)

        # Setup audit logger filehandler based on lofs_file.
        audit_logger_handler = logging.FileHandler(self.logs_file)
        self.audit_logger.addHandler(audit_logger_handler)

        # The definitions logger for writing the export defs.
        self.defs_logger = logging.getLogger(
            "defs_{}:{}".format(self.title, self.notebook))
        self.defs_logger.setLevel(logging.INFO)

        if self.write_defs:
            defs_logger_handler = logging.FileHandler(self.defs_file)
            self.defs_logger.addHandler(defs_logger_handler)

# -- Overriding __repr__ and __str__ -------------------------------------------

    def __repr__(self):
        return ("Publication({notebook}, {title}, "
                "formatter={formatter}, "
                "write_defs={write_defs}, "
                "overwrite={overwrite}, delete_log={delete_log}, "
                "root_path={root_path}, "
                "main_path={main_path}, "
                "figs_dir={figs_dir}, "
                "defs_dir={defs_dir}, "
                "data_dir={data_dir}, "
                "logs_dir={logs_dir}, "
                "definitions_file={definitions_file}, "
                "logs_file='_kallysto.log')").format(
            notebook=self.notebook,
            title=self.title,
            formatter=self.formatter,
            write_defs=self.write_defs,
            overwrite=self.overwrite,
            delete_log=self.delete_log,
            root_path=self.root_path,
            main_path=self.main_path,
            figs_dir=self.figs_dir,
            defs_dir=self.defs_dir,
            data_dir=self.data_dir,
            logs_dir=self.logs_dir,
            definitions_file=self.defs_file,)

    def __str__(self):
        return ("Locations:\n"
                "  {root_path}{title}/\n"
                "    {defs_path}{defs_file}\n"
                "    {figs_path}\n"
                "    {data_path}\n"
                "    {logs_path}{logs_file}\n"
                "Settings:\n"
                "  overwrite: {overwrite}\n"
                "  delete_log: {delete_log}\n"
                "  formatter: {formatter}\n"
                "  write_defs: {write_defs}").format(
            title=self.title,
            root_path=self.root_path,
            defs_path=self.defs_path,
            defs_file=self.defs_file.split('/')[-1],
            figs_path=self.figs_path,
            data_path=self.data_path,
            logs_path=self.logs_path,
            logs_file=self.logs_file.split('/')[-1],
            overwrite=self.overwrite,
            delete_log=self.delete_log,
            formatter=self.formatter,
            write_defs=self.write_defs,)

# -- Publication, Public API ----------------------------------------------------------------

    def export(self, export):
        """Export the definition and log the export.
        """

        # If write_defs then write definitions file.
        if self.write_defs:
            self.defs_logger.info(export.def_str)

        # Log the export.
        self.audit_logger.info(export.log_str)

        # Add the export to exports.
        self.exports.append(export)

        return export
