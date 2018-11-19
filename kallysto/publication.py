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
Create a publication link, connecting a notebook to a publication tree.

Creates a set of subfolders within a publication title folder inside
the publication root of the project.

The location of the publication root, relative to a notebook, and the
names of the created subfolders can be configured through the constructor.

Additional configuration options include: whether or not to overwrite
existing folders/files/logs; whether to create seperate definition files; when
definition files are to be created, which formatter to use.

Example Usage:

The following doctests check the basic publication setup by creating two
publication targets.

>>> from kallysto.publication import Publication

# Create a new publication as an export target (interim_report). It is assumed
# this code is run in a notebook (notebook_0) and that the interim_report is
# located at 'tests/sandbox/' relative to the notebook.
>>> interim = Publication('notebook_0', 'interim_report', write_defs=False, \
rel_pub_path='tests/sandbox/', overwrite=True, delete_log=True)

# Create another publication as an export target (final_report). It is assumed
# this code is run in a notebook (notebook_1) and that the final_report is
# located at 'tests/sandbox/' relative to the notebook.
>>> final = Publication('notebook_1', 'final_report', \
rel_pub_path='tests/sandbox/', overwrite=True, delete_log=True)

>>> interim
Publication(notebook_0, interim_report, formatter=<class \
'kallysto.formatter.Latex'>, write_defs=False, overwrite=True, \
delete_log=True, rel_pub_path=tests/sandbox/, main_path=../../, figs_dir=figs/, \
defs_dir=defs/, data_dir=data/, logs_dir=logs/, \
definitions_file=tests/sandbox/interim_report/defs/notebook_0/_definitions.tex,\
 logs_file='_kallysto.log')
>>> final
Publication(notebook_1, final_report, formatter=<class \
'kallysto.formatter.Latex'>, write_defs=True, overwrite=True, \
delete_log=True, rel_pub_path=tests/sandbox/, main_path=../../, figs_dir=figs/, \
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

# -- Publication ---------------------------------------------------------

import logging
import os
from shutil import rmtree
from kallysto.formatter import Latex
from kallysto.export import Export

class Publication(object):
    """Create a link (export path) to a given publication.

    This creates a directory called `title` at `rel_pub_path`, setting up
    subdirectories inside it for data/, defs/, figs/, and logs/, which will
    hold corresponding export objects. The names of these subdirectories,
    and associated files (`defs_file` and `logs_file`), are configurable
    as params of the publication link constructor. The `overwrite` and
    `delete_log` params control whether existing data is overwritten or left
    in place when the publication link is created.

        """

# -- Init ---------------------------------------------------------------------

    def __init__(self, notebook, title,

                 formatter=Latex,

                 write_defs=True,

                 overwrite=False, delete_log=False,

                 # Default configuration settings.
#                  nb_path=os.getcwd(),      # the abs path to the current/calling nb.
                 rel_pub_path='../../pubs/',  # From notebook to pubs root
#                  main_path='../../',       # From main.tex to pubs root
#                  figs_dir='figs/',
#                  defs_dir='defs/',
#                  data_dir='data/',
#                  logs_dir='logs/',
#                  tex_dir='tex/',
#                  defs_filename='_definitions.tex',
#                  logs_filename='_kallysto.log',
                ):

        """Constructor for a new pub, connecting a notebook to pub title.

        Args:
            notebook: the name/nickname for the source nb.
            title: creates a subdir of this name in pub root.

            write_defs: defintions file created? (needed for Latex. If False
            then no definitions file is created but figs/data are still exported,
            which can be useful if (manually) importing in other pub formats.

            overwrite: overwrite existing publications files/dirs?
            delete_log: delete existing log?

            rel_pub_path: relative path from notebook to publication root (pubs/).
            main_path: relative path from main .tex to root (pubs/).

            figs_dir: directory name for fig exports.
            data_dir: directory name for data exports (for tables & figures)
            defs_dir: directory name for export definitions.
            logs_dir: directory name for log.

            defs_file: name of definitions file.
            logs_file: name of log file.

        """
        
        # A simple display logger that writes progress to screen.
        self.display_logger = logging.getLogger(
            "Kallysto:{}:{}: ".format(title, notebook))
        self.display_logger.setLevel(logging.INFO)

        self.exports = []  # Exports sent to the pub.

        self.formatter = formatter

        self.write_defs = write_defs
        self.title = title
        self.notebook = notebook

        self.nb_path = os.getcwd()
                 
        self.rel_pub_path = rel_pub_path
        self.main_path = '../../'
        self.defs_dir = 'defs/'
        self.logs_dir = 'logs/'
        self.figs_dir = 'figs/'
        self.data_dir = 'data/'
        self.tex_dir = 'tex/'

        self.defs_filename = '_definitions.tex'
        self.logs_filename = '_kallysto.log'
        self.kallysto_filename = 'kallysto.tex'

        # Cleanup/overwrite existing publication.
        self.overwrite = overwrite
        self.delete_log = delete_log

        if self.overwrite:
            self.cleanup_notebook_files()

        # Create/setup the notebook directories.
        self.setup_notebook_directories()

        # Setup logging; defs logger and audit logger.
        self.setup_logging()

        # Update kallysto.tex include file.
        self.update_kallyso_includes()

# -- @properties ---------------------------------------------------------

    # The following properties define paths to the various directories to be
    # used to store different types, and components of, exports associated
    # with a given notebook.

   
    @property
    def figs_path(self):
        return "{}{}/{}{}/".format(
            self.rel_pub_path, self.title, self.figs_dir, self.notebook)

    @property
    def defs_path(self):
        return "{}{}/{}{}/".format(
            self.rel_pub_path, self.title, self.defs_dir, self.notebook)

    @property
    def data_path(self):
        return "{}{}/{}{}/".format(
            self.rel_pub_path, self.title, self.data_dir, self.notebook)

    @property
    def logs_path(self):
        return "{}{}/{}".format(
            self.rel_pub_path, self.title, self.logs_dir)

    @property
    def defs_file(self):
        return self.defs_path + self.defs_filename

    @property
    def logs_file(self):
        return self.logs_path + self.logs_filename
    
    @property
    def kallysto_path(self):
        return '{}{}/{}'.format(
            self.rel_pub_path, self.title, self.tex_dir)
    
    @property
    def kallysto_file(self):
        return self.kallysto_path + self.kallysto_filename

    @property
    def notebook_path(self):
        return os.path.relpath(os.getcwd(), start=self.logs_path)
    
    @property
    def notebook_file(self):
        return self.notebook_path + '/' + self.notebook
    
    
        


# -- Init Helpers --------------------------------------------------------

    def cleanup_notebook_files(self):
        """Cleanup existing publication files if they exist.

        Delete folders (figs, data, etc) and files associated with the
        current publication, but do not delete the central log unless
        expressly indicated by delete_log.
        
        Note: does not cleanup tex_dir as this is assumed to contain user
        generate files.

        Args:
            delete_log: delete central log file?
        """

        self.display_logger.info(
            'Removing export files for %s:%s', self.title, self.notebook)

        # If delete_log == True then delete log file.
        if self.delete_log:
            if os.path.isfile(self.logs_file):
                try:
                    self.display_logger.info(
                        'Trying to remove %s.', self.logs_file)

                    os.remove(self.logs_file)

                    self.display_logger.info(
                        'Removed %s.', self.logs_file)

                except OSError:
                    self.display_logger.warning(
                        'Could not remove %s', self.logs_file)
            else:
                self.display_logger.info(
                    '%s did not exist.', self.logs_file)


        if os.path.isfile(self.defs_file):

            # Remove notebook definitions file, if it exists.
            try:
                self.display_logger.info(
                    'Trying to remove %s.', self.defs_file)

                os.remove(self.defs_file)

                self.display_logger.info(
                    'Removed %s.', self.defs_file)

            except OSError:
                self.display_logger.warning(
                    'Could not remove %s.', self.defs_file)

        else:
            self.display_logger.info(
                '%s did not exist.', self.defs_file)

        # Prepare to remove the notebook folders for defs, figs and data.
        folders = [self.defs_path, self.figs_path, self.data_path]
        if self.delete_log:
            folders.append(self.logs_path)

        # Next, delete the folders themselves.
        for folder in folders:
            try:
                self.display_logger.info('Trying to remove %s.', folder)
                rmtree(folder)
                self.display_logger.info('Removed %s.', folder)

            except OSError:
                self.display_logger.info(
                    'Failed to remove %s. Probably no directory.', folder)


    def setup_notebook_directories(self):
        """Create the folders and files for a new publication."""

        self.display_logger.info(
            'Creating export locations for %s:%s.', self.title, self.notebook)

        # Create main root if it doesn't exist;  top-level pubs directory.
        self.display_logger.info('Creating %s.', self.rel_pub_path)
        os.makedirs(self.rel_pub_path, exist_ok=True)

        # Create the title if it doesn't exist;
        # self.pubroot = root/title/, top-level folder for this pub title.
        self.display_logger.info('Creating %s%s.', self.rel_pub_path, self.title)
        os.makedirs(self.rel_pub_path + self.title, exist_ok=True)

        # Prepare to create main folders ...
        folders = [self.figs_path, self.data_path, self.logs_path, self.kallysto_path]

        # Add defs folder if definitions are to be written.
        if self.write_defs:
            folders.append(self.defs_path)

        # Create main folders for defs, figs, data and logs if necessary.
        for folder in folders:
            self.display_logger.info('Creating %s.', folder)
            os.makedirs(folder, exist_ok=True)

        # Create the definitions file if needed.
        if self.write_defs:
            self.display_logger.info(
                'Creating %s if it does not exist.', self.defs_file)
            open(self.defs_file, 'a').close()

        # Create logs file.
        self.display_logger.info(
            'Creating %s if it does not exist.', self.logs_file)
        open(self.logs_file, 'a').close()
        
        # Create kallysto file if it does not exist.
        if not os.path.isfile(self.kallysto_file):
            self.display_logger.info(
            'Creating %s as it does not exist.', self.kallysto_file)
            open(self.kallysto_file, 'a').close()
            
        

    def setup_logging(self):
        """Setup Kallysto's logging.

        Kallysto uses three loggers:
        (1) A display logger for info messages, setup in init;
        (2) an audit logger to log exports to a central publication log file;
        (3) a defs logger for writing the export defintions; if needed.
        """

        # A file-based logger to create an kallysto audit trail.
        self.audit_logger = logging.getLogger(
            "audit_{}:{}".format(self.title, self.notebook))
        self.audit_logger.setLevel(logging.INFO)

        # Setup audit logger filehandler based on lofs_file.
        audit_logger_handler = logging.FileHandler(self.logs_file)
        self.audit_logger.addHandler(audit_logger_handler)

        # The definitions logger for writing the export defs.
        if self.write_defs:
            self.defs_logger = logging.getLogger(
                "defs_{}:{}".format(self.title, self.notebook))
            self.defs_logger.setLevel(logging.INFO)
            defs_logger_handler = logging.FileHandler(self.defs_file)
            self.defs_logger.addHandler(defs_logger_handler)


    def update_kallyso_includes(self):
        """Add an include statetment for current notebook in kallysto.tex"""

#         # The path to the main .tex file.
#         kallysto_path = '{}{}/{}kallysto.tex'.format(
#             self.rel_pub_path, self.title, self.tex_dir)

        include = Latex.include(self)

        # Append a Latex include to the defs file for the publication/notebook.
        with open(self.kallysto_file, "r") as kallysto:
            all_includes = kallysto.read()

            # If the current include is not in the file then add it.
            if include not in all_includes:
                all_includes = all_includes+include

        with open(self.kallysto_file, "w") as kallysto:
            kallysto.write(all_includes)

# -- Overriding __repr__ and __str__ -------------------------------------

    def __repr__(self):
        return ("Publication({notebook}, {title}, "
                "formatter={formatter}, "
                "write_defs={write_defs}, "
                "overwrite={overwrite}, delete_log={delete_log}, "
                "rel_pub_path={rel_pub_path}, "
                "main_path={main_path}, "
                "figs_dir={figs_dir}, "
                "defs_dir={defs_dir}, "
                "data_dir={data_dir}, "
                "logs_dir={logs_dir}, "
                "definitions_file={definitions_file}, "
                "logs_file='_kallysto.log', "
                "tex_dir={tex_dir})").format(
                    notebook=self.notebook,
                    title=self.title,
                    formatter=self.formatter,
                    write_defs=self.write_defs,
                    overwrite=self.overwrite,
                    delete_log=self.delete_log,
                    rel_pub_path=self.rel_pub_path,
                    main_path=self.main_path,
                    figs_dir=self.figs_dir,
                    defs_dir=self.defs_dir,
                    data_dir=self.data_dir,
                    logs_dir=self.logs_dir,
                    definitions_file=self.defs_file,
                    tex_dir=self.tex_dir)

    def __str__(self):
        return ("Locations:\n"
                "  {rel_pub_path}{title}/\n"
                "    {defs_path}{defs_file}\n"
                "    {figs_path}\n"
                "    {data_path}\n"
                "    {logs_path}{logs_file}\n"
                "  {main_path}\n"
                "    {kallysto_file}\n"
                "Settings:\n"
                "  overwrite: {overwrite}\n"
                "  delete_log: {delete_log}\n"
                "  formatter: {formatter}\n"
                "  write_defs: {write_defs}").format(
                    title=self.title,
                    rel_pub_path=self.rel_pub_path,
                    defs_path=self.defs_path,
                    defs_file=self.defs_file.split('/')[-1],
                    figs_path=self.figs_path,
                    data_path=self.data_path,
                    logs_path=self.logs_path,
                    logs_file=self.logs_file.split('/')[-1],
                    main_path=self.main_path,
                    kallysto_file=self.kallysto_file,
                    overwrite=self.overwrite,
                    delete_log=self.delete_log,
                    formatter=self.formatter,
                    write_defs=self.write_defs,)

# -- Publication, Public API ---------------------------------------------

    def export(self, export):
        """Export the definition and log the export."""

        # If write_defs then write definitions file.
        if self.write_defs:
            self.defs_logger.info(export.def_str)

        # Log the export.
        self.audit_logger.info(export.log_str)

        # Add the export to exports.
        self.exports.append(export)

        return export
