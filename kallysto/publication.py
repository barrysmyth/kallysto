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

# -- Publication ---------------------------------------------------------

import logging
import os
from shutil import rmtree

from kallysto.formatter import Latex, Markdown
from kallysto.export import Export

class Publication(object):
    """Managing links from a notebook script to Kallysto publication for exports.
    """

# -- Init ---------------------------------------------------------------------

    def __init__(self, notebook, title,
                 formatter='latex',
                 write_defs=True,
                 overwrite=False, fresh_start=False,
                 pub_root='../../pubs',  # From notebook to pubs root
                ):

        """Create a new link from the current notebook/script to a Kallysto publciation.

        Args:
            notebook: the name/nickname for the source nb; used in Kallysto meta-data.
            title: the name of the target publications; used to create the
            Kallysto (file-based) data store for the publication.

            formatter: the formatter to create Kallysto 'defintiions'
            
            write_defs: create an export definitions file?

            overwrite: overwrite existing data store? (leaves log intact)
            fresh_start: delete data store and log.

            pub_root: path from notebook to publication root; the publication data 
            store (title) will be created inside the pub_root.

        """
        
        # A simple display logger that writes progress to screen.
        self.display_logger = logging.getLogger(
            "Kallysto:{}:{}: ".format(title, notebook))
        self.display_logger.setLevel(logging.INFO)

        self.formatter = Latex if formatter=='latex' else Markdown

        self.write_defs = write_defs
        
        self.title, self.notebook = title, notebook        
        
        # Key Kallyso locations; at various times paths will be needed from/to
        # the nb and pub roots.
        self.nb_root = os.getcwd() # The location of the current notebook/script.
        self.pub_root = os.path.abspath(pub_root)
        
        # Key Kallysto data store paths to data, figs, defs, logs, tex components. 
        self.data_path= 'data/' + self.notebook
        self.figs_path = 'figs/' + self.notebook
        self.defs_path, self.defs_filename = 'defs/' + self.notebook, self.formatter.defs_filename
        self.src_path, self.kallysto_filename  = self.formatter.src_path, self.formatter.includes_filename
        self.logs_path, self.logs_filename = 'logs/', 'kallysto.log'
                

        # Cleanup the data store as required.
        self.overwrite = overwrite
        self.fresh_start = fresh_start

        if self.overwrite or self.fresh_start:
            self.cleanup_data_store()

        # Create/setup the Kallysto data store.
        self.setup_data_store()

        # Setup logging; defs logger and audit logger.
        self.setup_logging()

        # Update kallysto.tex include file.
        self.update_kallyso_includes()

            
# -- Init Helpers --------------------------------------------------------

    def cleanup_data_store(self):
        """Cleanup the Kallysto data store for the current publication.
        """

        self.display_logger.info(
            'Removing export files for %s:%s', self.title, self.notebook)

        # If fresh_start then delete log dir amd kallysto.tex.
        if self.fresh_start:
            
            self.safely_remove_dir(self.path_to(self.logs_path))
            
            kallysto_file = self.path_to(self.src_path + '/' + self.kallysto_filename)
            self.safely_remove_file(kallysto_file)
        
        # Delete defs, figs, and data dirs, and their contents.
        [self.safely_remove_dir(self.path_to(folder))
         for folder in [self.defs_path, self.figs_path, self.data_path]]

        
    def setup_data_store(self):
        """Setup the Kallysto directories and files needed for the data store.
        """

        self.display_logger.info(
            'Creating export locations for %s:%s.', self.title, self.notebook)

        # Create the pub_root if it doesn't exist.
        self.display_logger.info('Creating %s.', self.pub_root)
        os.makedirs(self.pub_root, exist_ok=True)

        # Create the target publication, if it doesn't exist;
        pub_title = self.pub_root + '/' + self.title
        self.display_logger.info('Creating %s.', pub_title)
        os.makedirs(pub_title, exist_ok=True)

        # Create main kallysto folders (inside the target publication root)
        # for figs, data, defs, logs
        [os.makedirs(self.path_to(folder), exist_ok=True)
         for folder in [self.defs_path, self.figs_path, self.data_path, self.logs_path]]
        
        # Create a blank definitions file, but only if needed.
        if self.write_defs:
            defs_file = self.path_to(self.defs_path + '/' + self.defs_filename)
            self.display_logger.info('Creating %s if it does not exist.', defs_file)
            open(defs_file, 'a').close()

        # Create the Kallysto src folder.
        os.makedirs(self.path_to(self.src_path), exist_ok=True)
        
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
        """Add an `\input` statetment for current notebook in kallysto.tex
        
        The kallysto.tex file contains the Latex instructions to include 
        any of the defintions files that habve been created by notebooks
        exporting to the target publication. Each exporting notebook will
        provide one defintions file. 
    
        The purpose of this kallysto.tex file is to make it easy for users
        to include their exports in the main Latex document, by including
        this single file (using `input`).
        """
        
        # The kallysto includes file.
        kallysto_file = self.path_to(self.src_path + '/' + self.kallysto_filename)
        
        # The  Latex include statment for the current defs file.
        current_include = self.formatter.include(self)
        
        # Open kallysto.tex for appending; create new file if necessary.
        with open(kallysto_file, "a+") as kallysto:
            
            kallysto.seek(0)  # return to top of file first.
            
            all_includes = kallysto.read()  # The current set of includes.
            
            # If the current include is not in the file
            # then add it. Else do nothing.
            if current_include not in all_includes:
                kallysto.write(current_include)  # Rewrite new include.


# -- Publication, Public API ---------------------------------------------

    def export(self, export):
        """Export the definition and log the export.
        
        Write the export defintion to the appropriate definitions file, if needed,
        log the export in the kallysto.log, and add the export object to the
        list of exports made for the publication.
        """

        # If write_defs then write definitions file.
        if self.write_defs:
            self.defs_logger.info(export.def_str)

        # Log the export.
        self.audit_logger.info(export.log_str)

        return export
    
    
    def path_to(self, to_dir, start=None):
        """Determine the path to pub_root/title/<to_dir> .
        
        If start==None then assume the path is needed fron nb_root,
        otherwise caluclate the path from start.
        
        Args:
            to_dir: target directory.
            start: start of path or None.
        """
        
        # A hack since cannot pass self.nb_root as a default arg.
        start = self.nb_root if start is None else start

        return os.path.relpath(self.pub_root + '/' + self.title + '/' + to_dir, start=start)

    def safely_remove_file(self, file):
        """Attempt to delete file; capture/notify exceptions as appropriate.
        
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