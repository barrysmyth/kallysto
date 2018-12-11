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
    """Link a notebook to a publication and its Kallysto export datastore.
    
    A Publication instance creates a specific link from a notebook to a target
    publication and its associated Kallysto datastore. A given notebook can
    create many different publication links so that exports can be sent to
    different publications.
    
    Each Publication is associated with a type, either Latex or Markdown, which
    determines how the exports will be defined so that they can be imported
    available to the publication. For Latex publications, exports are defined
    as Latex commands in a definitions file, which is then imported into the 
    main Latex source file. Markdown does not allow for defintions as standard, 
    instead Kallysto adds a new import syntax to Markdown and provides a simple
    converter to handle the import process and generate standard Markdown.
    """

# -- Init ---------------------------------------------------------------------

    def __init__(self, notebook, title,
                 formatter=Latex,
                 write_defs=True,
                 overwrite=False, fresh_start=False,
                 pub_path='../../pubs/',  # From notebook to pubs root
                ):

        """Create a new link from the current notebook/script to a Kallysto publciation.

        Args:
            notebook: the name/nickname for the source nb; used in Kallysto meta-data.
            title: the name of the target publications; used to create the
            Kallysto (file-based) data store for the publication.

            formatter: the formatter to create Kallysto 'defintiions'
            
            write_defs: create an export definitions file?

            overwrite: overwrite existing data store? If true then the existing datastore,
            which may include exports from other notebooks, is deleted and recreated from
            scratch.
            
            fresh_start: remove Kallysto's includes file.

            pub_root: path from notebook to publication root; the publication data 
            store (title) will be created inside the pub_root.

        """
        
        # A simple display logger that writes progress to screen.
        self.display_logger = logging.getLogger(
            "Kallysto:{}:{}: ".format(title, notebook))
        self.display_logger.setLevel(logging.INFO)

        self.formatter = formatter

        self.write_defs = write_defs
        
        self.title, self.notebook = title, notebook        
        
        # Key Kallyso locations; at various times paths will be needed from/to
        # the nb and pub roots.
        self.nb_path = os.getcwd() + '/' # The location of the current notebook/script.
        self.notebook_file = self.nb_path + self.notebook
        
        self.pub_path = pub_path
        
        # Rel paths from calling notebook.
        self.kallysto_path = self.pub_path + '/' + self.title + '/' + '_kallysto/'
        
        # Key Kallysto data store paths and files. 
        self.data_path = self.kallysto_path + 'data/' + self.notebook + '/'
        self.figs_path = self.kallysto_path + 'figs/' + self.notebook + '/'
        self.defs_path = self.kallysto_path + 'defs/' + self.notebook + '/'
        self.logs_path = self.kallysto_path + 'logs/'

        self.defs_file = self.defs_path + self.formatter.defs_filename
        self.logs_file = self.logs_path + 'kallysto.log'
        
        # Publication src path, from the notebook.
        self.src_path = self.pub_path + self.title + '/' + self.formatter.src_path
        self.includes_file = self.src_path + self.formatter.includes_filename

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
        

    # Generating paths to files within the Kallysto datastore.
    def data_file(self, filename):
        """Generate the Kallyso datastore path to a data file."""
        return self.data_path + '/' + filename

    def fig_file(self, filename):
        """Generate the Kallyso datastore path to a fig/image file."""
        return self.figs_path + '/' + filename
    
            
# -- Init Helpers --------------------------------------------------------

    def cleanup_data_store(self):
        """Cleanup the Kallysto data store for the current publication.
        
        Delete the existing Kallysto datastore, if it exists and remove the
        log and includes file if required.
        """

        self.display_logger.info(
            'Removing datastore for %s:%s', self.title, self.notebook)

        # If fresh_start then remove the includes file and the logs file.
        if self.fresh_start:
            self.safely_remove_file(self.includes_file)
            self.safely_remove_file(self.logs_file)
        
        # Delete the Kallysto folders for the current notebook in the datastore.
        for folder in [self.data_path, self.figs_path, self.defs_path]:
            self.safely_remove_dir(folder)

        
    def setup_data_store(self):
        """Setup the Kallysto directories and files needed for the data store.
        
        The Kallysto data store is rooted by the `_kallysto` directory and
        includes sub directories for data, defs, figures, and logs.
        Exports are stored inside data/defs/figs, within a further layer of
        subdirs based on the name of the exporting notebook. The logs
        subdir contains a single logs file that logs all exports to the pub
        from multiple notebooks.
        """

        self.display_logger.info(
            'Creating export locations for %s:%s.', self.title, self.notebook)

        # Create the pub_root if it doesn't exist.
        self.display_logger.info('Creating %s.', self.pub_path)
        os.makedirs(self.pub_path, exist_ok=True)

        # Create the target publication, if it doesn't exist;
        pub_title = self.pub_path + '/' + self.title
        self.display_logger.info('Creating %s.', pub_title)
        os.makedirs(pub_title, exist_ok=True)
        
        # Create the datastore root.
        os.makedirs(self.kallysto_path, exist_ok=True)
        
        # Create the main datastore subdirs.
        [os.makedirs(folder, exist_ok=True)
         for folder in [self.defs_path, self.figs_path, self.data_path, self.logs_path]]
        
        # Create a blank definitions file, but only if needed.
        if self.write_defs:
            defs_file = self.defs_file
            self.display_logger.info('Creating %s if it does not exist.', defs_file)
            open(defs_file, 'a').close()

        # Create the Kallysto src folder.
        os.makedirs(self.src_path, exist_ok=True)
        
        # Create the log file.
        open(self.logs_file, 'a').close()


    def setup_logging(self):
        """Setup Kallysto's various loggers for reporting and logging to file."""

        # A file-based logger to create the Kallyso log.
        self.audit_logger = logging.getLogger(
            "audit_{}:{}".format(self.title, self.notebook))
        self.audit_logger.setLevel(logging.INFO)

        # Setup audit logger filehandler based on logs_file.
        audit_logger_handler = logging.FileHandler(self.logs_file)
        self.audit_logger.addHandler(audit_logger_handler)

        # The definitions logger for writing the export defs.
        if self.write_defs:
            self.defs_logger = logging.getLogger(
                "defs_{}:{}".format(self.title, self.notebook))
            self.defs_logger.setLevel(logging.INFO)
            defs_logger_handler = logging.FileHandler(
                self.defs_file)
            self.defs_logger.addHandler(defs_logger_handler)

    def update_kallyso_includes(self):
        """Update the publication's includes file.
        
        Each publication has an includes file which assembles all of
        the defintions files created by exports to the publication. By
        import this single includes file the target publication can 
        import all of the various defintions files that have been
        created by different exporting notebooks.
        """
        
        # The  Latex include statment for the current defs file.
        current_include = self.formatter.include(self)
        
        # Open kallysto.tex for appending; create new file if necessary.
        with open(self.includes_file, "a+") as kallysto:
            
            kallysto.seek(0)  # return to top of file first.
            
            all_includes = kallysto.read()  # The current set of includes.
            
            # If the current include is not in the file
            # then add it. Else do nothing.
            if current_include not in all_includes:
                kallysto.write(current_include)  # Rewrite new include.


# -- Publication, Public API ---------------------------------------------

    def export(self, export):
        """Write the export the definition and log the export.
        
        Write the export defintion to the appropriate definitions file, if needed,
        log the export in the kallysto.log.
        """

        # If write_defs then write definitions file.
        if self.write_defs:
            self.defs_logger.info(export.def_str)

        # Log the export.
        self.audit_logger.info(export.log_str)

        return export
    

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