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

import logging
import os
import sys
from time import time, strftime
from shutil import rmtree

from kallysto.formatter import Latex
from kallysto.export import Value, Table, Figure


class Publication():
    """Create a  bridge linking a notebook to a publication title.

    Creates a set of subfolders within a publication title folder inside
    the publication root of the project. The location of this publication
    root, relative to a notebook, and the names of the created
    subfolders can be configured through the constructor.

    Attributes:
        exports: a list of the export objects made for the bridge.
        value_template: the format specification for exporting a value.
        table_template: the format specification for exporting a table.
        figure_template: the format specification for exporting a figure.
        path: the path to the current notebook.
        root: the rel path from the notebook to the pub title's folder.
        title: the publication title.
        notebook: the notebook name.
        figs_dir: the name of the figure subfolder.
        data_dir: the name of the data subfolder.
        logs_dir: the name of the logs folder.
        defintions_file_name: the name of the source defintiions file.
        logs_file_name: the name of the central log file.
        pubroot: the path to the publication title.
        src: the path to the src subfolder.
        definitions_file: the path to the definitions file.
        figs: the path to the figs subfolder.
        data: the path to the data subfolder.
        logs: the path to the logs subfolder.
        log_file: the path to the central log file itself.
    """

    def __init__(self, notebook, title,

                 formatter=Latex,

                 overwrite=False, delete_log=False,

                 # Default configuration settings.
                 root_path='../../pubs/',  # From notebook to pubs root
                 main_path='../../',       # From main.tex to pubs root
                 figs_dir='figs/',
                 defs_dir='defs/',
                 data_dir='data/',
                 logs_dir='logs/',
                 definitions_file='_definitions.tex',
                 logs_file='_kallysto.log',):
        """Constructor for a new pub, connecting a notebook to pub title.

        Args:
            notebook: the notebook in which the bridge is created.
            title: the title of the publication.

            root: the location of the  publication root rel. to notebook.

            defs_dir: the name of the defintions subfolder (e.g. defs).
            figs_dir: the name of the subfolder to hold images for figs.
            data_dir: the subfolder to hold data files for tables/figs.
            logs_dir: the name of the subfolder holding the kallysto log.

            overwrite: If true delete pub folders and files for bridge.
            delete_log: If true rm log folder & file for the publication.
        """
        # A simple display logger that writes progress to screen.
        self.display_logger = logging.getLogger(
            "{}:{}".format(title, notebook))
        self.display_logger.setLevel(logging.INFO)

        self.exports = []  # To keep track of exports made thru pub.
        self.formatter = formatter

        # Setup  pub locations; i.e. paths to tex, data, figs, logs etc.
        self.setup_locations(title, notebook,
                             root_path, main_path,
                             defs_dir, logs_dir, figs_dir, data_dir,
                             definitions_file, logs_file)

        # If overwrite==True then delete files associated with the pub.
        if overwrite:
            self.cleanup_notebook_files(delete_log=delete_log)

        # Create/setup the notebook directories (src/figs/data/logs).
        self.setup_notebook_directories()

        # Setup logging; defs logger and audit logger.
        self.setup_logging()

        # Write to display/autid logs about the bridge creation.
        # self.log_bridge_setup()

    def setup_locations(self, title, notebook,
                        root_path, main_path,
                        defs_dir, logs_dir, figs_dir, data_dir,
                        definitions_file, logs_file):
        """Setting up locations for main folders (src/figs/data/logs).

        Creating and storing the paths to the src, figs, data, and logs
        subfolders, within the publication title root folder, with paths
        to the export definitions file and the main log file.
        """

        # Setting up basic bridge parameters:
        self.path = os.getcwd()  # Current (calling notebook) directory.

        self.title = title
        self.notebook = notebook

        self.root_path = root_path
        self.main_path = main_path

        self.figs_dir, self.data_dir = figs_dir, data_dir
        self.defs_dir, self.logs_dir = defs_dir, logs_dir

        # The paths from the notebook to the main folders.
        self.figs_path =\
            root_path + title + '/' + figs_dir + notebook + '/'
        self.defs_path =\
            root_path + title + '/' + defs_dir + notebook + '/'
        self.data_path =\
            root_path + title + '/' + data_dir + notebook + '/'

        self.logs_path = root_path + title + '/' + logs_dir

        self.defs_file = self.defs_path + definitions_file
        self.logs_file = self.logs_path + logs_file

    def cleanup_notebook_files(self, delete_log=False):
        """Cleanup existing bridge files if they exist.

        Delete folders and files associated with the current bridge. Dont
        delete the central log unless expressly indicated by delete_log.

        Args:
            delete_log: If True, delete central log file.
        """
        self.display_logger.info(
            'Removing export files for {}:{}'.format(
                self.title, self.notebook))

        # If delete_log == True then delete log file.
        if delete_log:
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
        if delete_log:
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
        """Create the folders and files for a new bridge."""

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

        # Create main folders for tex, figs, data and logs if necessary.
        for folder in [self.defs_path, self.figs_path,
                       self.data_path, self.logs_path]:
            self.display_logger.info('Creating {}.'.format(folder))
            os.makedirs(folder, exist_ok=True)

        # Create the definitions, log files if they don't already exist.
        self.display_logger.info(
            'Creating {} if it does not exist.'.format(self.defs_file))
        open(self.defs_file, 'a').close()

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

        defs_logger_handler = logging.FileHandler(self.defs_file)
        self.defs_logger.addHandler(defs_logger_handler)

    def __repr__(self):
        return ("{root_path}{title}/\n"
                "  {defs_path}{defs_file}\n"
                "  {figs_path}\n"
                "  {data_path}\n"
                "  {logs_path}{logs_file}\n").format(
            title=self.title,
            root_path=self.root_path,
            defs_path=self.defs_path,
            defs_file=self.defs_file.split('/')[-1],
            figs_path=self.figs_path,
            data_path=self.data_path,
            logs_path=self.logs_path,
            logs_file=self.logs_file.split('/')[-1])

    def export(self, export):
        """Export the definition and log the export.
        """

        self.defs_logger.info(export.def_str)
        self.audit_logger.info(export.log_str)

        self.exports.append(export)

    def delete(self):
        self.cleanup_notebook_files(delete_log=True)
