Kallysto --- Easy Python Exports
========

Export Python data from notebooks or scripts, for use in reports/publications.

Kallysto makes it easy to export values, tables, and figures for use in
reports or publications (Latex, markdown etc.)

An individual export will typically produce a definition, such as a Latex ``newcommand`` defintion, which can be imported into, and referenced in, the main publication file. Additional files, such as images (for figures) and source data files (figures and tables) are also exported.

Furthermore, in support of more
reproducible data science, Kallysto also creates a detailed audit trail for all exports.

As a quick-start, the following links to a publication called ``final`` and creates and pushes value, table, and figure exports:::

    final = Publication(
        'nb_1','final',
        root_path = '../../pubs/', formatter=Latex)

     mean_sales = Export.value('meanSales', df['sales'].mean())

     sales_table = Export.table('salesTable', df, caption='...')

     fig = df.plot().get_figure()
     sales_fig = Export.figure('salesFig', image=fig, data=df,
          caption='...')

     Export.to(final)

Usage
-----

Using Kallysto is a 3-step process:

**Step 1 - Connecting to a Publication**
Before anything can be exported, a notebook (or script) must be connected to a publication::

    final = Publication(
        'nb_1','final',
        root_path = '../../pubs/', formatter=Latex)

This creates a link from the notebook, ``nb_1`` to the publication, ``final``, located at ``../../pubs/`` relative to ``nb_1``, and uses the (default) Latex formatter. A set of folders and files is created as follows::

    pubs/final/
        - data/
            - nb_1/
        - defs/
            - nb_1/
                - definitions.tex
        - figs/
            - nb_1/
        - logs/
            - _kallysto.log

*Note*: a given notebook or script can be connected to multiple publications so that the same notebook or script can export to multiple publications.

**Step 2 - Creating the Exports**
Currently there are three types of exports: values (anything that can be rendered as a string), tables (Pandas dataframes), and figures (Matplotlib figures). For example, the following generates a value export (*mean_sales*), a table export (*sales_table*), and a sales graph ($sales_fig*).

    mean_sales = Export.value('meanSales', df['sales'].mean())

     sales_table = Export.table('salesTable', df, caption='Quarterly sales.')

     fig = df.plot().get_figure()
     sales_fig = Export.figure(
         'salesFig', image=fig, data=df,
          caption='Quarterly sales data.')

**Step 3 - Pushing the Exports**
Finally, we need to push the exports to our publication::

    mean_sales > final_report
     sales_table > final
     sales_fig > final

This creates Latex defintions in ``../../pubs/final/defs/nb_1/_definitions.tex`` with the necessary images and supporting data files stored in ``../../pubs/final/figs/nb_1/`` and ``../../pubs/final/data/nb_1/``, respectively.

    pubs/final/
        - data/
            - nb_1/
                sales_table.csv
                sales_fig.csv
        - defs/
            - nb_1/
                - definitions.tex
        - figs/
            - nb_1/
                sales_fig.pdf
        - logs/
            - _kallysto.log

*Note*: as a convenient alternative to pushing exports one at a time, it is possible to push all of the exports using ``Export.to(final)``.












Installation
------------

Requirements
------------

Compatibility
-------------

Licence
-------

Authors
-------

`kallysto` was written by `Barry Smyth <barry.smyth@ucd.ie>`_.
