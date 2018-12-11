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
# Permission
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
from collections import OrderedDict, namedtuple


from time import time, strftime
from datetime import datetime

import pandas as pd

# -- Export base class ---------------------------------------------------


class Export():
    """The base export class.

    An export is some item of data that can be exported to a publication
    and this base class is responsible for providing a simple constructor
    API and defining meta-data (id, name, creation date) that is common to
    all export types. 

    Creating an export with a name used by another export generates a warning
    and will fail, unless overwrite is True. Consequently we need a way to
    abort the object creation when the name is already taken and overwrite is
    False. To do this we override the objects __new__ constructor to perform
    the name check.

    Attributes:
        uid: unique id based on creation time.
        created: creation time.
        name: every export has a unique user-defined name, set at export time.
        def_str: the export defintion.
        log_str: the corresponding log message.
    """

    display_logger = logging.getLogger("Kallysto")
    
    
# -- Export creation ---------------------------------------------------------

    def __init__(self, name, export, cls):
        """Initialise new export.

        This base class constructor is not intended to be called directly
        but will be called by the constructors fof Value, Table, or Figure
        exports.
        """
        Export.display_logger.setLevel(logging.INFO)

        self.uid = time()                    # Unique id
        self.created = strftime('%X %x %Z')  # Creation data
        self.name = name                     # Export name

        self.def_str = None
        self.log_str = None

        # Add the new export object to the subclass export dict.
#         cls._exports[name] = self
        
        
    def __gt__(self, pub):
        """Export self to publication.
        
        This will not be called directly but rather from the
        corresponding method of one of the export subclasses.
        """
        return pub.export(self)

    
    def save_export_component(self, component, save_method, filepath):
        """Safely save an export component to the Kallysto data store.
        
        Write the export component to file in an appropriate format, 
        e.g. CSV for data or PDF for images. The component and an 
        appropriate save method (e.g. to_csv, or savefig) is provided 
        along with the file name and a check is made to ensure that 
        the save method is available with the particular component type.
        
        Args:
            component: export component such as data or a fig/image.
            save_method: a suitable method that can write the data to file.
            filepath: where to write the data.
        """
        
        # Check that the component has the save method.
        if hasattr(component, save_method):
            self.display_logger.info('Saving %s.', filepath)
            getattr(component, save_method)(filepath)
            
        else: 
            self.display_logger.warning(
                'Could not generate %s. Missing %s.', image_file_from_nb, save_method)

    
    def path_to(self, from_loc, to_loc):
        """Calculate the relative path from from_loc to to_loc."""
        
        return os.path.relpath(to_loc, start=from_loc)
    

# -- Export, Public API --------------------------------------------------

    # The following class methods provide a convenient public API
    # for Kallysto's main export functions (value, table, figue).

    @classmethod
    def value(cls, name, value, overwrite=True):
        """Create Value export with a name check."""
        return Value(name, value)

    @classmethod
    def table(cls, name, data, caption, overwrite=True):
        """Create Table export with a name check."""
        return Table(name, data, caption)

    @classmethod
    def figure(cls, name, image, data, caption, text_width=1, 
               format='pdf', overwrite=True):
        """Create Figure export with a name check."""
        return Figure(name, image, data, caption, text_width, format)
    

# -- Value ---------------------------------------------------------------


class Value(Export):
    """Export an atomic value (e.g. string/text, int, float etc.)

    A Value is the simplest type of export, and typically corresponds
    to a numeric value or string. Unlike other exports such as figures 
    and tables, a value export is not associated with any secondary
    data files (other than the Latex defintions file).

    Attributes:
        value: the value of the Python expression to be exported.
        data_file: the name of the export data file containing the value.
    """
#     _exports = OrderedDict()  # Dict of exports, keyed on name.

    def __init__(self, name, value):
        """
        Initialise a new Value instance and add to _exports.

        Args:
          name: the name of the export.
          value: the value of the export.
        """

        super().__init__(name, self, self.__class__)

        self.value = value
        self.data_file = "{}.txt".format(name)



# -- Override repr and str -----------------------------------------------

    def __repr__(self):
        return ('Value({name!r}, {value!r})').format(
            name=self.name,
            value=self.value)

    def __str__(self):
        return "VALUE,{uid},{created},{name},{value}".format(
            uid=self.uid, created=self.created,
            name=self.name, value=self.value)
    
    def gen_log_str(self, pub):
        
        # Set the log message.
        return ('{log_id},{logged},{title},{notebook},'
                        '{export},{data_path}').format(
                            log_id=self.uid,
                            logged=strftime('%X %x %Z'),
                            title=pub.title,
                            notebook=self.path_to(pub.logs_path, pub.notebook_file),
                            export=self.__class__.__name__,
                            data_path=self.path_to(pub.logs_path, pub.data_file(self.data_file))
        )

# -- Value, Public API ---------------------------------------------------

    def __gt__(self, pub):
        """Export self (Value) to publication.
        
        Generates the log string and call __gt__ in super to initiate
        the export 'transfer'.
        """

        # Set the definition string using the value formatter.
        self.def_str = pub.formatter.value(self, pub)

        self.log_str = self.gen_log_str(pub)

        # Save the value to a text file.
        # Note we cannot use `save_export_component` because the
        # data is a string and strings have no attribute to write
        # to a file and it seems unnecessary to wrap values in a new
        # class just to provide this.
        with open(pub.data_file(self.data_file), "w+") as value_file:
            value_file.write(str(self.value))
                    
        # Call the super __gt__ to complete the export transfer 
        # via Publciation (updating definitions, writing log etc.)
        return super().__gt__(pub)

# -- Table ---------------------------------------------------------------

class Table(Export):
    """Export a pandas dataframe as a table with the following components:

    name - the definition name to use.
    data - the dataframe.
    caption - the caption for the table.

    This  allows for the export of a standard pandas dataframe as a table.
    The appropriate snippet definition is created and added to the notebook's
    definition file. Also, the dataframe itself is saved as a .csv datafile.

    Attributes:
        data: the pandas dataframe.
        data_file: name of the data_file.
        caption: caption text for the table defintion.
    """
#     _exports = OrderedDict()  # Dict of exports, keyed on name.

# -- Table creation ------------------------------------------------------

    def __init__(self, name, data, caption):
        """
        Initialise a new Table.

        Args:
          name: name of the export.
          data: dataframe corresponding to the table.
          caption: table caption.
        """
        super().__init__(name, self, self.__class__)

        # The table-specific fields.
        self.data = data
        self.data_file = "{}.csv".format(name)
        self.caption = caption

# -- Override repr and str -----------------------------------------------

    def __repr__(self):
        return ('Table({name!r}, {data!r}, {caption!r})').format(
            name=self.name,
            data=self.data,
            caption=self.caption)

    def __str__(self):
        return "TABLE,{uid},{created},{name},{data_file}".format(
            uid=self.uid, created=self.created,
            name=self.name, data_file=self.data_file)
    
    def gen_log_str(self, pub):
        
        # Set the log message.
        return ('{log_id},{logged},{title},{notebook},'
                        '{export},{data_path}').format(
            log_id=self.uid,
            logged=strftime('%X %x %Z'),
            title=pub.title,
            notebook=self.path_to(pub.logs_path, pub.notebook_file),

            export=self.__class__.__name__, # TABLE
            
            # The path to the data file.
            data_path=self.path_to(pub.logs_path, pub.data_file(self.data_file))

        )
        

# -- Table, Public API ---------------------------------------------------

    def __gt__(self, pub):
        """Export self (Table) to publication
                
        This methods is responsible for (a) writing the csv file to hold
        the table data, (b) generating the log string and (c) calling 
        __gt__ in super to initiate the export 'transfer'.
        """

        # Set the definition string using the table formatter.
        self.def_str = pub.formatter.table(self, pub)
        
        # And the log string.
        self.log_str = self.gen_log_str(pub)
        
        # Save the data to .csv
        # The data is saved from the nb so needs to use path from nb.
        self.save_export_component(self.data, 'to_csv', pub.data_file(self.data_file))
        
        # Call the super __gt__ to complete the export transfer 
        # via Publciation (updating definitions, writing log etc.)
        return super().__gt__(pub)
    
    

# -- Figure ---------------------------------------------------------


class Figure(Export):
    """
    Export a matplotlib image as a figure, with the following components:

    name - name to use in definitions file.
    image - the figure image.
    data - the dataframe associated with the figure.
    caption - the caption for the figure.
    format - the format of the saved image (pdf or png)

    Attributes:
        data: the pandas dataframe related to the image.
        data_file: path to the data_file.
        image_file: path to the image_file.
        caption: caption text for the figure.
        format: the format of the image (e.g. pdf, png)
    """
#     _exports = OrderedDict()  # Dict of exports, keyed on name.

# -- Figure creation -----------------------------------------------------

    def __init__(self,
                 name, image, data, caption, text_width=1, format='pdf'):
        """Initialise a new Figure.

        Args:
          name: name of the export.
          image: the figure image.
          data: dataframe corresponding to teh table.
          caption: table caption.
          format: png or pdf.
        """

        super().__init__(name, self, self.__class__)

        # The figure-specific fields.
        self.image = image
        self.data = data
        self.caption = caption
        self.format = format
        self.text_width = text_width

        self.data_file = "{}.csv".format(name)          # The source-data file.
        self.image_file = "{}.{}".format(name, format)  # The figure image.

        self.fig_scale = 1     # Scaling of figures.

# -- Override repr and str -----------------------------------------------

    def __repr__(self):
        return ('Figure({name!r}, {image!r}, '
                '{data!r}, {caption!r}, {format!r})').format(
            name=self.name,
            image=self.image,
            data=self.data,
            caption=self.caption,
            format=self.format)

    def __str__(self):
        return "FIGURE,{uid},{created},{name},{image_file},{data_file}".format(
            uid=self.uid, created=self.created,
            name=self.name, image_file=self.image_file,
            data_file=self.data_file)
    
    def gen_log_str(self, pub):

        
        return ('{log_id},{logged},{title},{notebook},'
                        '{export},{figs_path},{data_path},').format(
            log_id=self.uid,
            logged=strftime('%X %x %Z'),
            title=pub.title,
            notebook=self.path_to(pub.logs_path, pub.notebook_file),

            figs_path=self.path_to(pub.logs_path, pub.fig_file(self.image_file)),
            data_path=self.path_to(pub.logs_path, pub.data_file(self.data_file)),

            export=self.__class__.__name__  # FIGURE
        )
        

# -- Figure, Public API --------------------------------------------------

    def __gt__(self, pub):
        """Export self (Figure) to publication.
                
        This methods is responsible for (a) writing the csv file to hold
        the table data, (b) generating the log string and (c) calling 
        __gt__ in super to initiate the export 'transfer'.
        """

        # Set the definition string using the figure formatter.
        self.def_str = pub.formatter.figure(self, pub)
    
        # Set the log message.
        self.log_str = self.gen_log_str(pub)
        
        # Paths to data/im
        # Save the data to .csv
        # The data is saved from the nb so needs to use path from nb.
        self.save_export_component(self.data, 'to_csv', pub.data_file(self.data_file))

        # Save the image.
        self.save_export_component(self.image, 'savefig', pub.fig_file(self.image_file))

        # Call the super __gt__ to complete the export transfer 
        # via Publciation (updating definitions, writing log etc.)
        return super().__gt__(pub)