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

from time import time, strftime
from datetime import datetime

import pandas as pd


class Export():
    """The base export class.

    Each export is associated with a unique id, a (Latex) name and a creation
    date.


    Attributes:
        uid: unique id based on creation time.
        created: creation time.
        name: every export has a user-defined name, set at export time.
        def_str: the export defintion.
        log_str: the corresponding log message.
    """

    @classmethod
    def all(cls):

        # Get subclasses of Export.
        subclasses = cls.__subclasses__()

        # Get the export dicts for these subclasses.
        dicts = [subclass.all() for subclass in subclasses]

        # Create a combined dict from all the exports
        all_exports = {key: val for d in dicts for key, val in d.items()}

        return all_exports

    def __init__(self, name, export, cls):
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

        # For convenience create a new builtin with same name as export.
        __builtins__[self.name] = self

        # Check is name is already used.
        if name in Export.all():
            raise ValueError(
                'Kallysto Error: Duplicate name, {}, is already used.'.format(
                    name))
        else:
            # Add the new export object to the appropriate subclass export list.
            cls._exports[name] = export

    def __gt__(self, publication):
        publication.export(self)


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

    _exports = {}  # Class var containing dict of exports, keyed on name.

    @classmethod
    def all(cls):
        return cls._exports

    def __init__(self, name, value):
        """
        Initialise a new Value instance.

        Args:
          bridge: A instance of a kallysto ridge.
        """

        super().__init__(name, self, self.__class__)

        self.value = value

    def __repr__(self):
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

        super().__gt__(publication)


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

    _exports = {}  # Class var containing dict of exports, keyed on name.

    @classmethod
    def all(cls):
        return cls._exports

    def __init__(self, name, data, caption):
        """
        Initialise a new Table.

        Args:
          name: name of the export.
          data: dataframe corresponding to teh table.
          caption: table caption.
        """
        super().__init__(name, self, self.__class__)

        self.data = data
        self.data_file = "{}.csv".format(name)
        self.caption = caption

    def __repr__(self):
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

        super().__gt__(publication)


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

    _exports = {}  # Class var containing dict of exports, keyed on name.

    @classmethod
    def all(cls):
        return cls._exports

    def __init__(self, name, image, data, caption, format):
        """
        Initialise a new Figure.

        Args:
          name: name of the export.
          image: the figure image.
          data: dataframe corresponding to teh table.
          caption: table caption.
          format: png or pdf.
        """

        super().__init__(name, self, self.__class__)

        self.image = image
        self.data = data
        self.caption = caption
        self.format = format

        # The data for the figure.
        self.data_file = "{}.csv".format(name)
        self.image_file = "{}.{}".format(name, format)  # The figure image.

        self.fig_scale = 1     # Scaling of figures.

    def __repr__(self):
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

        super().__gt__(publication)
