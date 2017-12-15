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

""" The basic export types used by Kallysto.

Each type of export represents a data structure to capture the key data
associated with the export type, whether a value, a figure or a table, for
example, so that the export may be 'exported' to a specific publication at some
future time. Typically this 'export' process will involve creating a definition
of the exported item (such as a latex defintion), which can be imported into a
publication, and a set of associated files, such as images and/or datafiles.

The Export class is the base class and provides a core set of functionality
shared by its subclasses (Value, table, Figure), which define the different
types of exports. For example, Export defines key attributes shared among the
different export types including, a unique id (uid), creation date (created),
unique export name (name) the export definition string (def_str), such as a
latex definition string, the log string (log_str) to be used in the Kallysto
log.

The Export class also manages a dict of created exports and is responsible for
ensuring that exports with duplicate names are managed correctly (either avoided
or overwritten).

    e.g. Export.list() -> returns a dict of created exports.
         Figure.list() -> returns a dict of created figures etc.

The Export class also includes functionality to allow all exports to be
exported to a given publication in bulk.

    e.g. Export.to(pub) -> exports all exports to pub.
         Table.to(pub) -> exports all tables to pub etc.

Currently there are three such subclasses -- Value, Table, and Figure -- and
each is associated with a particular set of attributes. Typically each export
is associated with a definition (e.g. a Latex \newcommand) so that the export
can be included in some publication source. Some exports (Table, Figure) are
also associated with secondary files such as images and data.

A Value export is simply a named Python (atomic) value such as a number or
string. In fact any Python expression that can be rendered as a string can
be exported as a value.

A Table export is a Pandas dataframe. In addition to a suitable export
defintion (e.g. a latex definition) a Table export is also associated with the
actual data which will be saved as a csv when the export is exported to a
publication. A Table export can also have a caption.

A Figure export is an image (e.g. a matpolotlib image). In addition to the
defintion (e.g. a Latex figure defintion) a Figure export is associated with
an image file (pdf/png) and a corresponding data file, saved as a csv upon
export to a publication, plus a caption.

Example Usage:

The follow doctests create a sample publication and then create and export
example value, table, and figure items to this publication.

>>> from kallysto.export import Export, Figure, Value, Table
>>> from kallysto.publication import Publication
>>> import pandas as pd
>>> import matplotlib.pylab as plt
>>> import numpy as np

# Create a new publication as an export target (final_report). It is assumed
# this code is run in a notebook (notebook_1) and that the final_report is
# located at 'tests/sandbox/' relative to the notebook.
>>> my_pub = Publication('notebook_1', 'final_report', root_path='tests/sandbox/')

# A sample dataframe of quarterly sales figures.
>>> df = pd.DataFrame([(1, 100),(2, 120),(3, 110),(4,200)],columns=['Qtr', 'Sales'])
>>> df
   Qtr  Sales
0    1    100
1    2    120
2    3    110
3    4    200

# An example Value export for the mean sales calculation.
>>> mean_sales = Value('valueMeanSales', df['Sales'].mean())
>>> mean_sales
Value('valueMeanSales', 132.5)
>>> mean_sales.value
132.5
>>> mean_sales.name
'valueMeanSales'
>>> mean_sales > my_pub
Value('valueMeanSales', 132.5)

# An example Table export for the dataframe.
>>> sales_table = Table('tableQuarterlySales', df, caption="Quartery sales table.")
>>> sales_table > my_pub
Table('tableQuarterlySales',    Qtr  Sales
0    1    100
1    2    120
2    3    110
3    4    200, 'Quartery sales table.')

# An example Figure export of sales vs quarter.
>>> fig, ax = plt.subplots()
>>> ax.plot(df['Qtr'], df['Sales'])  # doctest:+ELLIPSIS
[<matplotlib.lines.Line2D object at ...>]
>>> sales_fig = Figure('figQuarterlySales', image=fig, data=df, caption="Quarterly sales data.")
>>> sales_fig > my_pub  # doctest:+ELLIPSIS
Figure('figQuarterlySales', <matplotlib.figure.Figure ...>,    Qtr  Sales
...
3    4    200, 'Quarterly sales data.', 'pdf')

# All of the export objects created.
>>> Export.list()  # doctest:+ELLIPSIS
OrderedDict([('valueMeanSales', Value('valueMeanSales', 132.5)), ('tableQuarterlySales', Table('tableQuarterlySales',    Qtr  Sales
..., 'Quartery sales table.')), ('figQuarterlySales', Figure('figQuarterlySales', <matplotlib.figure.Figure object at ...>,    Qtr  Sales
..., 'Quarterly sales data.', 'pdf'))])

# Bulk export all of the exports.
>>> Export.to(my_pub)
['valueMeanSales', 'tableQuarterlySales', 'figQuarterlySales']

# It is also possible to bulk exports based on export type.
>>> Value.to(my_pub)
['valueMeanSales']
>>> Table.to(my_pub)
['tableQuarterlySales']
>>> Figure.to(my_pub)
['figQuarterlySales']
"""

import logging
import os
from collections import OrderedDict

from time import time, strftime
from datetime import datetime

import pandas as pd

# Some basic logging to display.
display_logger = logging.getLogger("Kallysto: ")
display_logger.setLevel(logging.INFO)


class Export():
    """The base export class.

    An export is a piece of data that is available for export.
    Each export is associated with a unique id, a name and a creation date.
    Exports are stored in the classvar _exports dict, keyed on export name.

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

    @classmethod
    def list(cls):
        """ Return a list of all exports as a dict keyed on name.

        The dict is generated dynamically from the _export classvars of all
        subclasses of Export.
        """

        # Get subclasses of Export.
        subclasses = cls.__subclasses__()

        # Get the export dicts for these subclasses.
        # dicts = [subclass.list() for subclass in subclasses]

        # Create a combined dict from all the exports
        all_exports = OrderedDict()
        for d in [subclass.list() for subclass in subclasses]:
            for name, export in d.items():
                all_exports[name] = export

        return all_exports

    @classmethod
    def to(cls, publication):
        """ Export all exports to publication.
        """

        for name, export in cls.list().items():
            export > publication

        return list(cls.list().keys())

    def __new__(cls, *args, **kwargs):
        """Create new export object subject to name-check.

        The object constructor. If the export name already exists and
        overwrite is False then generate a warning and don't return the object,
        which ensures the object is not created or initialised. Otherwise
        return the newly created object.

        This constructor will not be called directly but rather by Value,
        Table, Figure.
        """

        # Get the export name and overwrite status.
        name = args[0]  # Get the name of the export for namecheck.
        overwrite = kwargs['overwrite']

        # overwrite is false and name is used (a key in Export.list())...
        if (overwrite is False) & (name in Export.list()):

            # Log a warning message.
            display_logger.warn(
                ("Warning: name {} already in use for {!r}.\n"
                 "Use overwrite=True to override.").format(
                    name, Export.list()[name]))

            # Return None ensures object reation step is abandoned.
            return None

        # Otherwise, either the name is not used or overwrite is True so we
        # create the object and return it.
        else:
            obj = super(Export, cls).__new__(cls)
            return obj

    def __init__(self, name, export, cls, overwrite=False):
        """Initialise new export.

        This base class constructor is not intended to be called directly
        but will be called by the constructors fof Value, Table, or Figure
        exports.
        """

        self.uid = time()                    # Unique id
        self.created = strftime('%X %x %Z')  # Creation data
        self.name = name                     # Export name

        self.def_str = None
        self.log_str = None

        # Add the new export object to the subclass export dict.
        cls._exports[name] = self

        # self.update_export_list(name, export, cls, overwrite)

    def __gt__(self, publication):
        return publication.export(self)

    def update_export_list(self, name, export, overwrite):
        """Add new export to appropriate export dict.

        Update class-based export dict to incldue the new export if it does
        not already exist or is overwrite is True.
        if the name does already exist and overwrite is False then warn.
        """

        # Check is name is already used before updating _exports.
        if (overwrite is False) & (name in Export.list()):

            # Raise an error if the name is already used.
            display_logger.warn(
                ("Warning: name {} already in use for {!r}.\n"
                 "Use overwrite=True to override.").format(
                    name, Export.list()[name]))
        else:
            # Add the new export object to the subclass export dict.
            cls._exports[name] = export


class Value(Export):
    """Export an atomic value (e.g. string/text, int, float etc.)

    A Value  is the simplest type of export, and typically corresponds
    to a numeric value or string. Each Value export has a name and a
    corresponding value, which is used to create a new definition for the value
    which added to the corresponding notebook defintions file. Unlike other
    exports such as Figure or Table, a Value export is not associated with any
    secondary files (other than the defintions file).

    Attributes:
        value: the value of the Python expression to be exported.
    """
    _exports = OrderedDict()  # Dict of exports, keyed on name.

    @classmethod
    def list(cls):
        return cls._exports

    def __new__(cls, name, value, overwrite=False):
        return super(Value, cls).__new__(cls, name, value, overwrite=overwrite)

    def __init__(self, name, value, overwrite=False):
        """
        Initialise a new Value instance.

        Args:
          bridge: A instance of a kallysto ridge.
        """

        super().__init__(name, self, self.__class__, overwrite)

        self.value = value

    def __repr__(self):
        return ('Value({name!r}, {value!r})').format(
            name=self.name,
            value=self.value)

    def __str__(self):
        return "VALUE,{uid},{created},{name},{value}".format(
            uid=self.uid, created=self.created,
            name=self.name, value=self.value)

    def __gt__(self, publication):

        # Set the definition string.
        self.def_str = publication.formatter.value(self, publication)

        # Set the log message.
        self.log_str = ('{log_id},{logged},{title},{notebook},'
                        '{export}').format(
            log_id=time(),
            logged=strftime('%X %x %Z'),
            title=publication.title,
            notebook=publication.notebook,
            export=self)

        return super().__gt__(publication)


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
    _exports = OrderedDict()  # Dict of exports, keyed on name.

    @classmethod
    def list(cls):
        return cls._exports

    def __new__(cls, name, data, caption, overwrite=False):
        return super(Table, cls).__new__(
            cls, name, data, caption, overwrite=overwrite)

    def __init__(self, name, data, caption, overwrite=False):
        """
        Initialise a new Table.

        Args:
          name: name of the export.
          data: dataframe corresponding to teh table.
          caption: table caption.
        """
        super().__init__(name, self, self.__class__, overwrite)

        self.data = data
        self.data_file = "{}.csv".format(name)
        self.caption = caption

    def __repr__(self):
        return ('Table({name!r}, {data!r}, {caption!r})').format(
            name=self.name,
            data=self.data,
            caption=self.caption)

    def __str__(self):
        return "TABLE,{uid},{created},{name},{data_file}".format(
            uid=self.uid, created=self.created,
            name=self.name, data_file=self.data_file)

    def __gt__(self, publication):

        # Set the definition string.
        self.def_str = publication.formatter.table(self, publication)

        # Set the log message.
        self.log_str = ('{log_id},{logged},{title},{notebook},{data_path},'
                        '{export}').format(
            log_id=time(),
            logged=strftime('%X %x %Z'),
            title=publication.title,
            notebook=publication.notebook,
            data_path=publication.data_path,
            export=self)

        # Save the data to .csv
        self.data.to_csv(publication.data_path + self.data_file)

        return super().__gt__(publication)


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
    _exports = OrderedDict()  # Dict of exports, keyed on name.

    @classmethod
    def list(cls):
        return cls._exports

    def __new__(cls,
                name, image, data, caption, format='pdf', overwrite=False):
        return super(Figure, cls).__new__(cls,
                                          name, image, data, caption,
                                          format=format, overwrite=overwrite)

    def __init__(self,
                 name, image, data, caption, format='pdf', overwrite=False):
        """
        Initialise a new Figure.

        Args:
          name: name of the export.
          image: the figure image.
          data: dataframe corresponding to teh table.
          caption: table caption.
          format: png or pdf.
        """

        super().__init__(name, self, self.__class__, overwrite)

        self.image = image
        self.data = data
        self.caption = caption
        self.format = format

        # The data for the figure.
        self.data_file = "{}.csv".format(name)
        self.image_file = "{}.{}".format(name, format)  # The figure image.

        self.fig_scale = 1     # Scaling of figures.

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

    def __gt__(self, publication):

        # Set the definition string.
        self.def_str = publication.formatter.figure(self, publication)

        # Set the log message.
        self.log_str = ('{log_id},{logged},{title},{notebook},'
                        '{figs_path},{data_path},{export}').format(
            log_id=time(),
            logged=strftime('%X %x %Z'),
            title=publication.title,
            notebook=publication.notebook,
            figs_path=publication.figs_path,
            data_path=publication.data_path,
            export=self)

        # Save the data to .csv
        self.data.to_csv(publication.data_path + self.data_file)

        # Save the image.
        self.image.savefig(publication.figs_path +
                           self.image_file, format=self.format)

        return super().__gt__(publication)
