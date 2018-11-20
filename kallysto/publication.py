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
                 overwrite=False, fresh_start=False,
                 pub_root='../../pubs',  # From notebook to pubs root
                ):

        """Constructor for a new pub, connecting a notebook to pub title.

        Args:
            notebook: the name/nickname for the source nb.
            title: creates a subdir of this name in pub root.

            formatter: the formatter to create 'defintiions'
            write_defs: defintions file created? (needed for Latex. If False
            then no definitions file is created but figs/data are still exported,
            which can be useful if (manually) importing in other pub formats.

            overwrite: overwrite existing publications files/dirs?
            delete_log: delete existing log?

            rel_pub_path: relative path from notebook to publication root (pubs/).

        """
        
        # A simple display logger that writes progress to screen.
        self.display_logger = logging.getLogger(
            "Kallysto:{}:{}: ".format(title, notebook))
        self.display_logger.setLevel(logging.INFO)

        self.exports = []  # Exports sent to the pub.

        self.formatter = formatter

        self.write_defs = write_defs
        
        # The publication title and the name of the source notebook.
        self.title, self.notebook = title, notebook        
        
        # Key directories; convert to absolute paths
        self.nb_root = os.getcwd()
        self.pub_root = os.path.abspath(pub_root)
        
        self.data_path= 'data/' + self.notebook
        self.figs_path = 'figs/' + self.notebook
        
        self.defs_path, self.defs_filename = 'defs/' + self.notebook, '_definitions.tex'
        self.tex_path, self.kallysto_filename  = 'tex', 'kallysto.tex'
        self.logs_path, self.logs_filename = 'logs/', 'kallysto.log'
                

        # Cleanup/overwrite existing publication.
        self.overwrite = overwrite
        self.fresh_start = fresh_start

        if self.overwrite:
            self.cleanup_notebook_files()



# -- Init Helpers --------------------------------------------------------

    def cleanup_notebook_files(self):
        """Cleanup existing publication files if they exist.

        Delete folders (figs, data, etc) and files associated with the
        current publication, but do not delete the central log unless
        expressly indicated by delete_log.
        
        Note: does not cleanup tex_dir as this is assumed to contain user
        generate files.
        """

        self.display_logger.info(
            'Removing export files for %s:%s', self.title, self.notebook)

        # If fresh_start then delete log dir amd kallysto.tex.
        if self.fresh_start:
            
            self.safely_remove_dir(self.path_to(self.logs_path))
            
            kallysto_file = self.path_to(self.tex_path + '/' + self.kallysto_filename)
            self.safely_remove_file(kallysto_file)
        
        # Delete defs, figs, and data dirs, and their contents.
        [self.safely_remove_dir(self.path_to(folder))
         for folder in [self.defs_path, self.figs_path, self.data_path]]
        
        # Create/setup the notebook directories.
        self.setup_notebook_directories()

        # Setup logging; defs logger and audit logger.
        self.setup_logging()

        # Update kallysto.tex include file.
        self.update_kallyso_includes()
        
        
        
    def setup_notebook_directories(self):
        """Create the folders and files for a new publication.
        
        This includes creating the publication root directory if it does not exist;
        adding the publication title subdirectory; creating the main kallysto folders
        for figs, data etc.; adding a definitions file if needed; creating the
        kallysto files for logging and .tex includes (if needed)
        """

        self.display_logger.info(
            'Creating export locations for %s:%s.', self.title, self.notebook)

        # Create <pub_root> if it doesn't exist;  top-level pubs directory.
        self.display_logger.info('Creating %s.', self.pub_root)
        os.makedirs(self.pub_root, exist_ok=True)

        # Create the <title> if it doesn't exist;
        pub_title = self.pub_root + '/' + self.title
        self.display_logger.info('Creating %s.', pub_title)
        os.makedirs(pub_title, exist_ok=True)

        # Create main kallysto folders for figs, data, defs, logs
        [os.makedirs(self.path_to(folder), exist_ok=True)
         for folder in [self.defs_path, self.figs_path, self.data_path, self.logs_path]]
        
        # Create the definitions file if needed.
        if self.write_defs:
            defs_file = self.path_to(self.defs_path + '/' + self.defs_filename)
            self.display_logger.info('Creating %s if it does not exist.', defs_file)
            open(defs_file, 'a').close()

        # Create kallysto tex folder and includes file if needed.
        if self.formatter == Latex:
            os.makedirs(self.path_to(self.tex_path), exist_ok=True)
            
            kallysto_file = self.path_to(self.tex_path + '/' + self.kallysto_filename)
            open(kallysto_file, 'a').close()
        
        # Create the log.
        log_file = self.path_to(self.logs_path + '/' + self.logs_filename)
        open(log_file, 'a').close()
        

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
        audit_logger_handler = logging.FileHandler(
            self.path_to(self.logs_path + '/' + self.logs_filename))
        self.audit_logger.addHandler(audit_logger_handler)

        # The definitions logger for writing the export defs.
        if self.write_defs:
            self.defs_logger = logging.getLogger(
                "defs_{}:{}".format(self.title, self.notebook))
            self.defs_logger.setLevel(logging.INFO)
            defs_logger_handler = logging.FileHandler(
                self.path_to(self.defs_path + '/' + self.defs_filename))
            self.defs_logger.addHandler(defs_logger_handler)


    def update_kallyso_includes(self):
        """Add an include statetment for current notebook in kallysto.tex"""
        
        include = Latex.include(self)

        # Append a Latex include to the defs file for the publication/notebook.
        with open(self.path_to(self.tex_path + '/' + self.kallysto_filename), "r") as kallysto:
            all_includes = kallysto.read()

            # If the current include is not in the file then add it.
            if include not in all_includes:
                all_includes = all_includes+include

        with open(self.path_to(self.tex_path + '/' + self.kallysto_filename), "w") as kallysto:
            kallysto.write(all_includes)

# -- Overriding __repr__ and __str__ -------------------------------------

#     def __repr__(self):
#         return ("Publication({notebook}, {title}, "
#                 "formatter={formatter}, "
#                 "write_defs={write_defs}, "
#                 "overwrite={overwrite}, delete_log={delete_log}, "
#                 "rel_pub_path={rel_pub_path}, "
#                 "main_path={main_path}, "
#                 "figs_dir={figs_dir}, "
#                 "defs_dir={defs_dir}, "
#                 "data_dir={data_dir}, "
#                 "logs_dir={logs_dir}, "
#                 "definitions_file={definitions_file}, "
#                 "logs_file='_kallysto.log', "
#                 "tex_dir={tex_dir})").format(
#                     notebook=self.notebook,
#                     title=self.title,
#                     formatter=self.formatter,
#                     write_defs=self.write_defs,
#                     overwrite=self.overwrite,
#                     delete_log=self.delete_log,
#                     rel_pub_path=self.rel_pub_path,
#                     main_path=self.main_path,
#                     figs_dir=self.figs_dir,
#                     defs_dir=self.defs_dir,
#                     data_dir=self.data_dir,
#                     logs_dir=self.logs_dir,
#                     definitions_file=self.defs_file,
#                     tex_dir=self.tex_dir)

#     def __str__(self):
#         return ("Locations:\n"
#                 "  {rel_pub_path}{title}/\n"
#                 "    {defs_path}{defs_file}\n"
#                 "    {figs_path}\n"
#                 "    {data_path}\n"
#                 "    {logs_path}{logs_file}\n"
#                 "  {main_path}\n"
#                 "    {kallysto_file}\n"
#                 "Settings:\n"
#                 "  overwrite: {overwrite}\n"
#                 "  delete_log: {delete_log}\n"
#                 "  formatter: {formatter}\n"
#                 "  write_defs: {write_defs}").format(
#                     title=self.title,
#                     rel_pub_path=self.rel_pub_path,
#                     defs_path=self.defs_path,
#                     defs_file=self.defs_file.split('/')[-1],
#                     figs_path=self.figs_path,
#                     data_path=self.data_path,
#                     logs_path=self.logs_path,
#                     logs_file=self.logs_file.split('/')[-1],
#                     main_path=self.main_path,
#                     kallysto_file=self.kallysto_file,
#                     overwrite=self.overwrite,
#                     delete_log=self.delete_log,
#                     formatter=self.formatter,
#                     write_defs=self.write_defs,)

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
    
    
    def path_to(self, to_dir, start=None):
        """Determine the path to to_dir (in pub_root) from nb_root."""
        
        # A hack since cannot pass self.nb_root as a default arg.
        start = self.nb_root if start is None else start

        return os.path.relpath(self.pub_root + '/' + self.title + '/' + to_dir, start=start)

    def safely_remove_file(self, file):
        """Safely attempt to delete file.
        
        Safely catch exceptions and log appropriate messages 
        based on outcome.
        """

        if os.path.isfile(file):
            try:
                self.display_logger.info('Trying to remove %s.', file)
                
                os.remove(file)
                
                self.display_logger.info('Removed %s.', file)

            except OSError:
                self.display_logger.warning('Could not remove %s', file)
        else:
            self.display_logger.info('%s did not exist.', file)
            
            
    def safely_remove_dir(self, folder):
        """Safely attempt to delete directory.
        
        Safely catch exceptions and log appropriate messages 
        based on outcome.
        """
        try:
            self.display_logger.info('Trying to remove %s.', folder)
            rmtree(folder)
            self.display_logger.info('Removed %s.', dir)

        except OSError:
            self.display_logger.info(
                'Failed to remove %s. Probably no directory.', folder)