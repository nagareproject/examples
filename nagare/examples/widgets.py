# -*- coding: iso-8859-1 -*-

#--
# Copyright (c) 2008-2012 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
#--


"""Examples of same reusable widgets"""

from __future__ import with_statement

import operator

from nagare import component, presentation, var

# -----------------------------------------------------------------------------------------

import time
import datetime

class Date(object):
    """A date widget to include into a ``<form>``
    """    
    months = (
                'january', 'february', 'mars', 'april',
                'may', 'june', 'july', 'august',
                'september', 'october', 'november', 'december'
             )

    def __init__(self, date):
        """Initialization
        
        In:
          - ``date`` -- a ``datetime`` object
        """
        self.day = var.Var(str(date.day))
        self.month = var.Var(str(date.month))
        self.year = var.Var(str(date.year))

    def to_datetime(self):
        """Return the data into a ``datetime`` object
        
        Return:
          - the datetime
        """
        return datetime.date(int(self.year()), int(self.month()), int(self.day()))

    def __str__(self):
        return str(self.to_datetime())
        
    @property
    def error(self):
        """Validate the date
        
        Return:
          - ``None`` if the date is valid else the error message
        """
        try:
            self.to_datetime()
            return None
        except ValueError, data:
            return str(data)

    def from_string(self, date):
        """Read a date from a string
        
        In:
          - ``date`` string with year, month and day (blank separator)
        """
        (year, month, day) = date.split()
        
        self.year(year)
        self.month(month)
        self.day(day)

@presentation.render_for(Date)
def render(self, h, *args):
    """Fragment to include in a ``<form>``
    """
    current_year = datetime.date.today().year
    
    return (
            h.select([h.option('%02d' % i, value=str(i)).selected(self.day()) for i in range(1, 32)]).action(self.day),
                 
            h.select([h.option(name, value=str(i+1)).selected(self.month()) for (i, name) in enumerate(Date.months)]).action(self.month),
                 
            h.select([h.option(i, value=str(i)).selected(self.year()) for i in range(current_year, current_year+5)]).action(self.year)
           )

# ---------------------------------------------------------------------------

class Table(object):
    """This component displays a table with sortable columns
    """
    def __init__(self, rows, headers, sortable_headers=(), colors=('white',), edit=None):
        """Initialization
        
        In:
          - ``rows`` -- the table data as list of lists
          - ``headers`` -- names of the columns
          - ``sortable_headers`` -- names of the sortable columns
          - ``colors`` -- list of background colors
          - ``edit`` -- callbacks function to edit
        """
        self.rows = rows
        self.headers = list(headers)
        self.sortable_headers = sortable_headers
        self.colors = colors
        self.edit = edit

        if len(sortable_headers) != 0:
            # By default, sort on the first sortable column
            self.sort_by(sortable_headers[0])
        else:
            # By default, sort on the first column
            self.sort_by(headers[0])

    def sort_by(self, name, reverse=False):
        """Criteria of the sort
        
        In:
          - ``name`` -- name of the column to sort
          - ``reverse`` -- sort in ascendant or descendant order
        """
        self.sort_header = name
        self.reverse = reverse
        i = self.headers.index(name)
        self.sort_criteria = lambda x: x[i]

    def sort(self, name):
        """Criteria of the sort
        
        In:
          - ``name`` -- name of the column to sort
        """
        reverse = False
        if self.sort_header == name:
            reverse = not self.reverse
        self.sort_by(name, reverse)

@presentation.render_for(Table)
def render(self, h, comp, *args):
    # List of the HTML for each header name
    headers = []
    for header in self.headers:
        if header in self.sortable_headers:
            # Sortable header: display its name in an active link
            headers.append(h.a(header).action(lambda name=header: self.sort(name)))
        else:
            # No sortable header: display only its name
            headers.append(header)
            
    with h.table(width='100%'):
        h << h.tr([h.th(header) for header in headers])

        # Sort and display the data
        for (i, row) in enumerate(sorted(self.rows, key=self.sort_criteria, reverse=self.reverse)):
            with h.tr(bgcolor=self.colors[i % len(self.colors)]):
                h << [h.td(column) for column in row]

                if self.edit is not None:
                    h << h.td(h.a('edit').action(lambda row=row: self.edit(comp, row)))

    return h.root

# ---------------------------------------------------------------------------

class BatchedTable(object):
    """This component displays a table with a given maximum number of rows and
    the classic ```previous`` and ``next`` actions
    """
    def __init__(self, rows, size, headers, colors=('white',)):
        """Initialization
        
        In:
          - ``rows`` -- the complete table data as list of lists
          - ``size`` - batch size (maximum number of rows displayed)
          - ``headers`` -- names of the columns
          - ``colors`` -- list of background colors
        """
        self.rows = rows
        self.offset = var.Var(0)
        self.size = size
        self.headers = list(headers)
        self.colors = colors
        
@presentation.render_for(BatchedTable)
def render(self, h, *args):
    # Dynamically create a ``Table`` component, with the subset of the data
    table = Table(
               self.rows[self.offset():self.offset()+self.size],
               self.headers, (),
               self.colors
               )
    
    # Display the table and the actions
    return (
            component.Component(table),
            h.a('<previous').action(lambda: self.offset(self.offset()-self.size)) if self.offset()-self.size >= 0 else '',
            ' | ',
            h.a('next>').action(lambda: self.offset(self.offset()+self.size)) if self.offset()+self.size < len(self.rows) else ''
           )

# ---------------------------------------------------------------------------

class SelectionTable(Table):
    """This component display a table with selectable rows and multiple actions
    
    It specializes the ``Table`` component
    """
    def __init__(self, *args, **kw):
        """Initialization
        
        In:
          - ``rows`` -- the table data as list of lists
          - ``headers`` -- names of the columns
          - ``sortable_headers`` -- names of the sortable columns
          - ``colors`` -- list of background colors
          - ``edit`` -- tuples (name to display, callback)
        """        
        super(SelectionTable, self).__init__(*args, **kw)
        self.reset_selected()   # After initialization, no row selected

    def reset_selected(self):
        """Deselect all the rows
        """
        self.selected = []
        
    def go(self, comp, f):
        """Call a function with the selected rows
        
        In:
           - ``comp`` - this component
           - ``f`` -- callback fonction to call
        """
        if len(self.selected) != 0:
            # Call the callback with all the rows and the selected ones
            f(comp, self.selected)
            self.reset_selected()
        
@presentation.render_for(SelectionTable)
def render(self, h, comp, *args):
    # List of the HTML for each header name    
    headers = []
    for header in self.headers:
        if header in self.sortable_headers:
            # Sortable header: display its name in an active link            
            headers.append(h.a(header).action(lambda name=header: self.sort(name)))
        else:
            # No sortable header: display only its name            
            headers.append(header)
    
    with h.form.pre_action(self.reset_selected):        
        with h.table:
            h << h.th()
            h << [h.th(header) for header in headers]
 
            # Sort and display the data   
            for (i, row) in enumerate(sorted(self.rows, key=self.sort_criteria, reverse=self.reverse)):
                with h.tr(bgcolor=self.colors[i % len(self.colors)]):
                    # Add a column with checkboxes
                    with h.td:
                        h << h.input(type='checkbox').action(lambda v, row=row: self.selected.append(row))
                        
                    h << [h.td(column) for column in row]
        
        # Display the action buttons
        h << [h.input(type='submit', value=name).action(lambda f=f: self.go(comp, f)) for (name, f) in self.edit]
            
        return h.root

    return h.root
