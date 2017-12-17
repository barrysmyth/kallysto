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

""" Kallysto Export Types.

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
>>> final = Publication('notebook_1', 'final_report', \
root_path='tests/sandbox/', overwrite=True, delete_log=True)

# A sample dataframe of quarterly sales figures.
>>> df = pd.DataFrame([(1, 100),(2, 120),(3, 110),(4,200)],\
columns=['Qtr', 'Sales'])
>>> df
   Qtr  Sales
0    1    100
1    2    120
2    3    110
3    4    200

# An example Value export for the mean sales calculation.
>>> mean_sales = Export.value('valueMeanSales', df['Sales'].mean())
>>> mean_sales
Value('valueMeanSales', 132.5)
>>> mean_sales.value
132.5
>>> mean_sales.name
'valueMeanSales'

# Creating an export with an existing name generates a warning.
>>> mean_sales = Export.value('valueMeanSales', df['Sales'].mean())
>>> mean_sales is Value.list()['valueMeanSales']
True
>>> mean_sales = Export.value('valueMeanSales', df['Sales'].mean(), overwrite=True)

>>> mean_sales > final
Value('valueMeanSales', 132.5)

# An example Table export for the dataframe.
>>> sales_table = Export.table('tableQuarterlySales', df, \
caption="Quartery sales table.")
>>> sales_table > final
Table('tableQuarterlySales',    Qtr  Sales
0    1    100
1    2    120
2    3    110
3    4    200, 'Quartery sales table.')

# An example Figure export of sales vs quarter.
>>> sales_fig = Export.figure(\
        'figQuarterlySales', image=df.plot().get_figure(), data=df,\
        caption='Quarterly sales data.')
>>> sales_fig > final  # doctest:+ELLIPSIS
Figure('figQuarterlySales', <matplotlib.figure.Figure ...
...
...

# List all of the export objects created.
>>> Export.list()  # doctest:+ELLIPSIS
OrderedDict([('valueMeanSales', Value('valueMeanSales', 132.5)), \
('tableQuarterlySales', Table('tableQuarterlySales',    Qtr  Sales
..., 'Quartery sales table.')), ('figQuarterlySales', \
Figure('figQuarterlySales', <matplotlib.figure.Figure object at ...
...
...

# Or we can get a list by type.
>>> Value.list()  # doctest:+ELLIPSIS
OrderedDict([('valueMeanSales', Value('valueMeanSales', 132.5))])

>>> Table.list()  # doctest:+ELLIPSIS
OrderedDict([('tableQuarterlySales', Table('tableQuarterlySales',...
...

>>> Figure.list()  # doctest:+ELLIPSIS
OrderedDict([('figQuarterlySales', Figure('figQuarterlySales', <matplotlib...
...

# Bulk export all of the exports.
>>> Export.to(final)
['valueMeanSales', 'tableQuarterlySales', 'figQuarterlySales']

# It is also possible to bulk exports based on export type.
>>> Value.to(final)
['valueMeanSales']
>>> Table.to(final)
['tableQuarterlySales']
>>> Figure.to(final)
['figQuarterlySales']
"""

import logging
import os
import sys
from collections import OrderedDict, namedtuple

from time import time, strftime
from datetime import datetime

import pandas as pd

# Some basic logging to display.
# display_logger = logging.getLogger("Kallysto")
# display_logger.setLevel(logging.INFO)

# -- Export base class ----------------------------------------------------------------------


class Export():
    """The base export class.

    An export is a piece of data that can be published to a publication.
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

    display_logger = logging.getLogger("Kallysto")
    _exports = OrderedDict()

# -- Export, public API -----------------------------------------

    @classmethod
    def value(cls, name, value, overwrite=False):
        """Create Value export with a name check."""
        existing = Export.name_exists(name, overwrite, cls.list())
        return existing if existing else Value(name, value)

    @classmethod
    def table(cls, name, data, caption, overwrite=False):
        """Create Table export with a name check."""
        existing = Export.name_exists(name, overwrite, cls.list())
        return existing if existing else Table(name, data, caption)

    @classmethod
    def figure(cls, name, image, data, caption, format='pdf', overwrite=False):
        """Create Figure export with a name check."""
        existing = Export.name_exists(name, overwrite, cls.list())
        return existing if existing else Figure(name, image, data, caption, format)

    @classmethod
    def list(cls):
        return cls._exports

# -- Util ---------------------------------------------------------

    @staticmethod
    def name_exists(name, overwrite, exports):
        """ If the name exists return the corresponding export."""

        if (not overwrite) & (name in exports):
            Export.display_logger.warn(
                ("Kallysto: "
                 "Export with name {} already in use for {!r}.\n"
                 "Use overwrite=True to override.").format(
                    name, exports[name]))

            return exports[name]

        return False


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
        cls._exports[name] = self

# -- Export, Public API ---------------------------------------------------------

    @classmethod
    def list(cls):
        """ Return a list of all exports as a dict keyed on name.

        When called from Export, the dict is generated dynamically from the
        _export class vars of all subclasses of Export. When called from a
        subclass the contents of _exports are used directly.
        """

        # If called from Export then build exports from subclasses' _exports.
        if cls == Export:

            # Create a combined dict from all the exports
            all_exports = OrderedDict()
            for d in [subclass.list() for subclass in cls.__subclasses__()]:
                for name, export in d.items():
                    all_exports[name] = export

            return all_exports

        # Else, if called by a subclass just return _exports.
        else:
            return cls._exports

    @classmethod
    def to(cls, publication):
        """ Export all exports in cls.list() to publication."""

        for name, export in cls.list().items():
            export > publication

        return list(cls.list().keys())  # Return export names for convenience.

    def __gt__(self, publication):
        """Export self to publication."""
        return publication.export(self)

# -- Value ---------------------------------------------------------------------


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

    def __init__(self, name, value):
        """
        Initialise a new Value instance and add to _exports.

        Args:
          name: the name of the export.
          value: the value of the export.
          overwrite: If True overwrite existing named export. Otherwise if the
                     name already exists then and overwrite is False then abort
                     the Value creation and warn the user.
        """

        super().__init__(name, self, self.__class__)

        # The value-specific fields; just value.
        self.value = value

# -- Override repr and str -----------------------------------------------------

    def __repr__(self):
        return ('Value({name!r}, {value!r})').format(
            name=self.name,
            value=self.value)

    def __str__(self):
        return "VALUE,{uid},{created},{name},{value}".format(
            uid=self.uid, created=self.created,
            name=self.name, value=self.value)

# -- Value, Public API ----------------------------------------------------------

    def __gt__(self, publication):
        """Export self (Value) to publication."""

        # Set the definition string using the value formatter.
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

# -- Table ---------------------------------------------------------------------


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

# -- Table creation ------------------------------------------------------------

    def __init__(self, name, data, caption):
        """
        Initialise a new Table.

        Args:
          name: name of the export.
          data: dataframe corresponding to teh table.
          caption: table caption.
          overwrite: If True overwrite existing named export. Otherwise if the
                     name already exists then and overwrite is False then abort
                     the Table creation and warn the user.
        """
        super().__init__(name, self, self.__class__)

        # The table-specific fields.
        self.data = data
        self.data_file = "{}.csv".format(name)
        self.caption = caption

# -- Override repr and str -----------------------------------------------------

    def __repr__(self):
        return ('Table({name!r}, {data!r}, {caption!r})').format(
            name=self.name,
            data=self.data,
            caption=self.caption)

    def __str__(self):
        return "TABLE,{uid},{created},{name},{data_file}".format(
            uid=self.uid, created=self.created,
            name=self.name, data_file=self.data_file)

# -- Table, Public API ----------------------------------------------------------

    def __gt__(self, publication):
        """Export self (Table) to publication"""

        # Set the definition string using the table formatter.
        self.def_str = publication.formatter.table(self, publication)

        # Set the log message.
        self.log_str = ('{log_id},{logged},{title},{notebook},'
                        '{export},{data_path}').format(
            log_id=time(),
            logged=strftime('%X %x %Z'),
            title=publication.title,
            notebook=publication.notebook,
            export=self,
            data_path=publication.data_path)

        # Save the data to .csv
        self.data.to_csv(publication.data_path + self.data_file)

        return super().__gt__(publication)

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
    _exports = OrderedDict()  # Dict of exports, keyed on name.

# -- Figure creation -----------------------------------------------------------

    def __init__(self,
                 name, image, data, caption, format='pdf'):
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

        self.data_file = "{}.csv".format(name)          # The source-data file.
        self.image_file = "{}.{}".format(name, format)  # The figure image.

        self.fig_scale = 1     # Scaling of figures.

# -- Override repr and str -----------------------------------------------------

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

# -- Figure, Public API ---------------------------------------------------------

    def __gt__(self, publication):
        """Export self (Figure) to publication"""

        # Set the definition string using the figure formatter.
        self.def_str = publication.formatter.figure(self, publication)

        # Set the log message.
        self.log_str = ('{log_id},{logged},{title},{notebook},'
                        '{export},{figs_path},{data_path},').format(
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
