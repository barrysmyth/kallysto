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

"""Formatters to produce export defintiions.

Formatters are responsible for producing the export definitions. Each
exportable object requires a separate exporter. Each exporter is implemented
as a static method associated with a user-defined formatter class. For example
below we define a Latex formatter class with methods for value, table, and
figure fromatters. Each formatter method accepts an export object and a
publication object as arguments so that the formatted definition can refer to
data from the export object or the publication."""

import os
import pandas as pd
from time import time, strftime
from tabulate import tabulate

# -- For Latex exports ---------------------------------------------------------

class Formatter():
    
    def __init__(self):
        pass
        
class Latex():
    """Generate formatted latex definitions for exports.

    Each definition is implemented as a Latex \newcommand. But in fact we
    use a combination of \providecommand and \renewcommand defs because this
    way we can force latex to use the last defintions to allow for repeat
    exports; it ensures that more recent exports overwrite earlier ones."""
    
    src_path = 'tex/'                    # The src latex dir
    includes_filename = 'kallysto.tex'  # The name of the includes file
    defs_filename = '_definitions.tex'
    

    @staticmethod
    def value(export, pub):
        msg = ('% Uid: {uid}\n'
               '% Created: {created}\n'
               '% Exported: {exported}\n'
               '% Title: {title}\n'
               '% Notebook: {notebook}\n'
               '% Data file: {data_file}\n'
               '\\providecommand{{\{name}}}{{\n'
               'dummy}}\n'
               '\\renewcommand{{\{name}}}{{\n'
               '{value}}}\n\n')
        
        return msg.format(uid=export.uid,
                          created=export.created,
                          exported=strftime('%X %x %Z'),
                          title=pub.title,
                          notebook=export.path_to(pub.src_path, pub.notebook_file),
                          data_file=export.path_to(pub.src_path, pub.data_file(export.data_file)),       
                          name=export.name,
                          value=export.value)

    @staticmethod
    def table(export, pub):
        msg = ('% Uid: {uid}\n'
               '% Created: {created}\n'
               '% Exported: {exported}\n'
               '% Title: {title}\n'
               '% Notebook: {notebook}\n'
               '% Data file: {data_file}\n'
               '\\providecommand{{\{name}}}{{\n'
               'dummy}}\n'
               '\\renewcommand{{\{name}}}{{\n'
               '    \\begin{{table}}[h]\n'
               '        \\centering\n'
               '        {definition}\n'
               '        \\caption{{{caption}}}\n'
               '        \\label{{{name}}}\n'
               '    \\end{{table}}\n'
               '}}\n\n')
        
        indented = '\t\t\t'.join(export.data.to_latex().splitlines(True))
        
        return msg.format(uid=export.uid,
                          created=export.created,
                          exported=strftime('%X %x %Z'),
                          title=pub.title,
                          notebook=export.path_to(pub.src_path, pub.notebook_file),
                          data_file=export.path_to(pub.src_path, pub.data_file(export.data_file)), 
                          name=export.name,
                          caption=export.caption,
                          definition=indented)

    @staticmethod
    def figure(export, pub):
        msg = ('% Uid: {uid}\n'
               '% Created: {created}\n'
               '% Exported: {exported}\n'
               '% Title: {title}\n'
               '% Notebook: {notebook}\n'
               '% Image file: {image_file}\n'
               '% Data file: {data_file}\n'
               '\\providecommand{{\{name}}}{{\n'
               'dummy}}\n'
               '\\renewcommand{{\{name}}}{{\n'
               '    \\begin{{figure}}\n'
               '        \\center\n'
               '        \\includegraphics[width={text_width}\\textwidth]'
               '{{{image_file}}}\n'
               '        \\caption{{{caption}}}\n'
               '        \\label{{{name}}}\n'
               '    \\end{{figure}}\n'
               '}}\n\n')

        return msg.format(uid=export.uid,
                          created=export.created,
                          exported=strftime('%X %x %Z'),
                          title=pub.title,
                          notebook=export.path_to(pub.src_path, pub.notebook_file),
                          data_file=export.path_to(pub.src_path, pub.data_file(export.data_file)), 
                          name=export.name,
                          text_width=export.text_width,
                          caption=export.caption,
                          image_file=export.path_to(pub.src_path, pub.fig_file(export.image_file)))

    @staticmethod
    def include(pub):
        """Generate the includes string for the current notebook's defs file."""

        path_to_defs = os.path.relpath(pub.defs_file, start=pub.src_path)

        msg = '\\input{{{}}}\n'.format(path_to_defs)

        return msg


    
class Markdown():
    
    src_path = 'md/'                    # The src markdown dir
    includes_filename = 'kallysto.kmd'  # The name of the includes file
    defs_filename = '_definitions.kmd'


    @staticmethod
    def value(export, pub):
        msg = ('% Uid: {uid}\n'
               '% Created: {created}\n'
               '% Exported: {exported}\n'
               '% Title: {title}\n'
               '% Notebook: {notebook}\n'
               '% Data file: {data_file}\n'
               '{{{name}:{value}}}\n\n')
        
        return msg.format(uid=export.uid,
                          created=export.created,
                          exported=strftime('%X %x %Z'),
                          title=pub.title,
                          notebook=export.path_to(pub.src_path, pub.notebook_file),
                          data_file=export.path_to(pub.src_path, pub.data_file(export.data_file)),          
                          name=export.name,
                          value=export.value)

    @staticmethod
    def table(export, pub):
        msg = ('% Uid: {uid}\n'
               '% Created: {created}\n'
               '% Exported: {exported}\n'
               '% Title: {title}\n'
               '% Notebook: {notebook}\n'
               '% Data file: {data_file}\n'
               '{{{name}:{definition}}}\n\n')

        # For the table definition we use tabulate to produce a simple
        # ascii based table which befores the defintion.
        def_str = tabulate(export.data, headers='keys', tablefmt='pipe')
        
        return msg.format(uid=export.uid,
                          created=export.created,
                          exported=strftime('%X %x %Z'),
                          title=pub.title,
                          notebook=export.path_to(pub.src_path, pub.notebook_file),
                          data_file=export.path_to(pub.src_path, pub.data_file(export.data_file)),   
                          name=export.name,
                          definition=def_str)

    @staticmethod
    def figure(export, pub):
        msg = ('% Uid: {uid}\n'
               '% Created: {created}\n'
               '% Exported: {exported}\n'
               '% Title: {title}\n'
               '% Notebook: {notebook}\n'
               '% Image file: {image_file}\n'
               '% Data file: {data_file}\n'
               '{{{name}:{definition}}}\n\n')

        def_str = '![{}]({} "{}")'.format(
            export.name, 
            export.path_to(pub.src_path, pub.fig_file(export.image_file)), 
            export.caption)
        
        return msg.format(uid=export.uid,
                          created=export.created,
                          exported=strftime('%X %x %Z'),
                          title=pub.title,
                          notebook=export.path_to(pub.src_path, pub.notebook_file),
                          data_file=export.path_to(pub.src_path, pub.data_file(export.data_file)),
                          image_file=export.path_to(pub.src_path, pub.fig_file(export.image_file)),
                          name=export.name,
                          definition=def_str)


    @staticmethod
    def include(pub):

        # The path to the defintiions file from the kallysto.tex file 
        # inside the tex dir.
        
        path_to_defs = os.path.relpath(pub.defs_file, start=pub.src_path)

        msg = '{}'.format(path_to_defs)

        return msg


