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

import pandas as pd
from time import time, strftime


class Latex():
    """Generate formatted latex definitions for exports.

    Each definition is implemented as a Latex \newcommand. But in fact we
    use a combination of \providecommand and \renewcommand defs because this
    way we can force latex to use the last defintions to allow for repeat
    exports; it ensures that more recent exports overwrite earlier ones."""

    @staticmethod
    def value(export, publication):
        msg = ('% Uid: {uid}\n'
               '% Created: {created}\n'
               '% Exported: {exported}\n'
               '% Title: {title}\n'
               '% Notebook: {notebook}\n'
               '\\providecommand{{\{name}}}\n{{dummy}}\n'
               '\\renewcommand{{\{name}}}\n{{{value}}}\n\n')

        return msg.format(uid=export.uid,
                          created=export.created,
                          exported=strftime('%X %x %Z'),
                          title=publication.title,
                          notebook=publication.notebook,
                          name=export.name,
                          value=export.value)

    @staticmethod
    def table(export, publication):
        msg = ('% Uid: {uid}\n'
               '% Created: {created}\n'
               '% Exported: {exported}\n'
               '% Title: {title}\n'
               '% Notebook: {notebook}\n'
               '\\providecommand{{\{name}}}\n{{dummy}}\n'
               '\\renewcommand{{\{name}}}{{\n\\begin{{table}}[h]\n'
               '{definition}\caption{{{caption}}}\n'
               '\label{{tab:{name}}}\\end{{table}}}}\n\n')

        return msg.format(uid=export.uid,
                          created=export.created,
                          exported=strftime('%X %x %Z'),
                          title=publication.title,
                          notebook=publication.notebook,
                          name=export.name,
                          caption=export.caption,
                          definition=export.data.to_latex())

    @staticmethod
    def figure(export, publication):
        msg = ('% Uid: {uid}\n'
               '% Created: {created}\n'
               '% Exported: {exported}\n'
               '% Title: {title}\n'
               '% Notebook: {notebook}\n'
               '\\providecommand{{\{name}}}\n{{dummy}}\n'
               '\\renewcommand{{\{name}}}{{\n\\begin{{figure}}\n'
               '\\includegraphics[width=1\\textwidth]'
               '{{{image_file}}}\n\\caption{{{caption}}}\n'
               '\\label{{{name}}}\n\\end{{figure}}}}\n\n')

        return msg.format(uid=export.uid,
                          created=export.created,
                          exported=strftime('%X %x %Z'),
                          title=publication.title,
                          notebook=publication.notebook,
                          name=export.name,
                          caption=export.caption,
                          image_file=publication.main_path +
                          publication.title + '/' +
                          publication.figs_dir +
                          publication.notebook + '/' + export.image_file)
