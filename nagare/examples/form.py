# -*- coding: iso-8859-1 -*-

#--
# Copyright (c) 2008-2012 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
#--

"""Forms with validation rules"""

from __future__ import with_statement

import datetime

from nagare import component, presentation, var, editor, validator
from nagare.examples import widgets

# --------------------------------------------------------------------------

class Form(object):
    """Object to edit"""
    def __init__(self):
        self.age = 20
        self.area = 'abcd'
        self.big = True
        self.medium = False
        self.small = True
        self.gender = 'male'
        self.color = ['blue', 'red']
        self.password = 'secret'
        self.file = None


class FormEditor(editor.Editor):
    """The form editor"""

    # The attributes of the target object, to edit
    fields = ('age', 'area', 'big', 'medium', 'small', 'gender', 'color', 'password')

    def __init__(self, target):
        """Initialization

        Create a ``editor.property`` for each ``self.fields`` of the target object

        In:
          - ``target`` -- the object to edit
        """
        super(FormEditor, self).__init__(target, self.fields)

        # Set the conversion and validation rules on the properties
        self.age.validate(lambda v: validator.to_int(v).lesser_than(50).greater_than(10).to_int())
        self.area.validate(lambda v: validator.to_string(v, strip=True).not_empty().match(r'^[a-d]+$').to_string())

        # A property can also be manually created
        self.file = editor.Property().validate(self.validate_file)

        # An editor can have more properties than the attributes of the target object
        self.confirm = editor.Property('').validate(self.validate_confirm)

    def validate_file(self, f):
        """A file is uploaded

        In:
          - ``f`` -- file object
        """
        if isinstance(f, basestring):
            return None

        return f.value

    def validate_confirm(self, v):
        """Validation of 2 related fields

        In:
          - ``v`` -- value of the ``confirm`` property

        Return:
          - ``v`` or raise an ``ValueError`` exception
        """
        if self.password() != v:
            raise ValueError('Confirm password different than password')

        return v

    def commit(self):
        """If the all properties have a valid value, write back the values
        into the target objects attributes
        """
        # Validate the ``self.fields`` properties and the ``confirm`` property
        # If they are all valid, commit the ``self.fields`` values and the
        # uploaded file content if it exits
        f = self.file.value

        if super(FormEditor, self).commit(self.fields, ('confirm',)) and f:
            self.target.file = f

    def reset_values(self):
        """Before to process the form data, the ``<option>`` and ``<checkbox>``
        properties need to be reseted
        """
        self.big(False)
        self.medium(False)
        self.small(False)

        self.color([])

# ---------------------------------------------------------------------------

# This example illustrates:
#
#  - the use of an intermediary editor object between the inputs received and
#    the target object.
#  - the association of validation methods to editor properties
#  - the highlighting of erroneous fields
#

@presentation.render_for(FormEditor)
def render(self, h, *args):
    #    print ">>>", self.age(), self.target.age, type(self.age()), type(self.target.age)

    h.head.css_url('form.css')

    # The ``pre_action`` of the ``<form>`` element is used to reset some data
    with h.form.pre_action(self.reset_values).post_action(self.commit):

        h << 'Age (between 10 and 50): ' << h.input(value=self.age()).action(self.age).error(self.age.error)
        h << h.br

        with h.fieldset:
            h << h.legend('A set of controls')

            h << 'A text (use only "[a-d]" characters):'
            h << h.textarea(self.area(), rows='2', cols='40').action(self.area).error(self.area.error)
            h << h.br << h.br

            h << 'Big' << h.input(type='checkbox').selected(self.big()).action(self.big)
            h << 'Medium' << h.input(type='checkbox').selected(self.medium()).action(self.medium)
            h << 'Small' << h.input(type='checkbox').selected(self.small()).action(self.small)
            h << h.br

            h << 'Male'
            h << h.input(type='radio', name='gender').selected(self.gender()=='male').action(lambda: self.gender('male'))
            h << ' Female'
            h << h.input(type='radio', name='gender').selected(self.gender()=='female').action(lambda: self.gender('female'))

        with h.select(multiple='multiple').action(self.color):
            with h.optgroup(label='Colors'):
                h << h.option('blue', value='blue').selected(self.color())
                h << h.option('white', value='white').selected(self.color())
            h << h.option('red', value='red').selected(self.color())
        h << h.br << h.br

        h << 'Upload a file:' << h.input(type='file').action(self.file) << h.br

        h << 'Password:' << h.input(type='password', length=10).action(self.password)
        h << ' '
        h << 'Confirm:' << h.input(type='password', length=10).action(self.confirm).error(self.confirm.error)
        h << h.hr

        h << h.input(type='submit', value='Go')

    return h.root

def example1():
    # Create a ``Form`` object, wrap it into a ``FormEditor`` and make it
    # a component
    return component.Component(FormEditor(Form()))

examples = ('Form with validation rules and "inline" error notifications', example1)

# ---------------------------------------------------------------------------

# This example illustrates:
#
#  - the use of an intermediary editor object between the inputs received and
#    the target object.
#  - the association of validation methods to editor properties
#  - the aggregation of all the errors notifications

@presentation.render_for(FormEditor, model='errors')
def render(self, h, *args):
    h.head.css_url('form.css')

    h.head.css('form-errors', '''
    .errors {
        border-top: 2px solid #c30;
        border-bottom: 2px solid #c30;
        background-color: #FFD5D5;
        margin: 8px;
    }

    .errors ol {
        margin: 4px 0 4px 0;
    }

    .errors ol li {
        font-size: 60%;
        font-weight: bold;
    }
    ''')

    errors = [(name, error) for (name, error) in (
                                                     ('Age', self.age.error),
                                                     ('Text', self.area.error),
                                                     ('Password', self.confirm.error)
                                                 ) if error]

    if len(errors):
        with h.div(class_='errors'):
            h << h.ol([h.li('%s: %s' % error) for error in errors])

    # The ``pre_action`` of the ``<form>`` element is used to reset some data
    with h.form.pre_action(self.reset_values).post_action(self.commit):
        h << 'Age (between 10 and 50): ' << h.input(value=self.age()).action(self.age)
        h << h.br

        with h.fieldset:
            h << h.legend('A set of controls')

            h << 'A text (use only "[a-d]" characters):'
            h << h.textarea(self.area(), rows='2', cols='40').action(self.area)
            h << h.br << h.br

            h << 'Big' << h.input(type='checkbox').selected(self.big()).action(self.big)
            h << 'Medium' << h.input(type='checkbox').selected(self.medium()).action(self.medium)
            h << 'Small' << h.input(type='checkbox').selected(self.small()).action(self.small)
            h << h.br

            h << 'Male'
            h << h.input(type='radio', name='gender').selected(self.gender()=='male').action(lambda: self.gender('male'))
            h << ' Female'
            h << h.input(type='radio', name='gender').selected(self.gender()=='female').action(lambda: self.gender('female'))

        with h.select(multiple='multiple').action(self.color):
            with h.optgroup(label='Colors'):
                h << h.option('blue', value='blue').selected(self.color())
                h << h.option('white', value='white').selected(self.color())
            h << h.option('red', value='red').selected(self.color())
        h << h.br << h.br

        h << 'Upload a file:' << h.input(type='file').action(self.file) << h.br

        h << 'Password:' << h.input(type='password', length=10).action(self.password)
        h << ' '
        h << 'Confirm:' << h.input(type='password', length=10).action(self.confirm)
        h << h.hr

        h << h.input(type='submit', value='Go')

    return h.root


class App:
    def __init__(self):
        self.editor = component.Component(FormEditor(Form()))

@presentation.render_for(App)
def render(self, h, *args):
    return self.editor.render(h, model='errors')

examples += ('Form with validation rules and error notifications', App)

# --------------------------------------------------------------------------

# This example illustrates the use of a predefined widget

class NameEditor(object):
    """An editor for a single text field
    """
    def __init__(self, name):
        """Initialization

        In:
          - ``name`` -- initial value of the text field
        """
        # Create a property. The text must be not empty
        self.name = editor.Property(name).validate(lambda v: validator.to_string(v, strip=True).not_empty().to_string())

    def commit(self, comp):
        """If no error, answer the text

        In:
          - ``comp`` -- the component
        """
        if not self.name.error:
            comp.answer(self.name())

@presentation.render_for(NameEditor)
def render(self, h, comp, *args):
    h.head.css_url('form.css')

    with h.form:
        h << 'Name: ' << h.input(value=self.name()).action(self.name).error(self.name.error)

        # On submit, the component answers the text
        h << h.input(type='submit', value='Change').action(lambda: self.commit(comp)) << ' '

        # On cancel, the component answers ``None``
        h << h.input(type='submit', value='Cancel').action(comp.answer)

        return h.root

def edit_name(comp, row):
    """Edit the field ``name`` of a row (field #1)

    In:
       - ``comp`` -- the current component
       - ``row`` -- a complete row

    Out:
      - ``row`` -- field ``name`` modified
    """
    # Fetch the field #1, wrap it into a ``NameEditor`` object and then make
    # it a component that replaces the current component
    name = comp.call(component.Component(NameEditor(row[1])))

    # The ``NameEditor`` answers the new field value
    # or ``None`` if the edition was canceled
    if name is not None:
        row[1] = name

def example2():
    headers = ('id', 'name')        # Name of the fields

    rows = [[2, 'a'], [3, 'b'], [1, 'c']]   # Table to display and edit

    # Create an object that display a table
    table = widgets.Table(
                          rows,                          # The data
                          headers,                       # Names of the fields
                          sortable_headers=headers,      # Names of the sortable fields
                          colors=('lightblue', 'white'), # The background of the displayed lines cycle on these colors
                          edit=edit_name                 # Callback to edit a line
                         )

    return component.Component(table)

examples += ('Sortable data grid', example2)

# --------------------------------------------------------------------------

# This example illustrates the use of a predefined widget

def example3():
    headers = ('id', 'name')        # Name of the fields

    rows = [(i, chr((i % 26)+97)*5) for i in range(1, 51)]
    table = widgets.BatchedTable(rows, 12, headers, colors=('lightblue', 'white'))

    return component.Component(table)

examples += ('Batched data grid', example3)

# --------------------------------------------------------------------------

class NamesEditor(object):
    """An editor for multiple text fields
    """
    def __init__(self, names):
        """Initialization

        Create an editor property for each names

        In:
          - ``names`` -- list of name to edit
        """
        self.names = [editor.Property(name).validate(lambda v: validator.to_string(v, strip=True).not_empty().to_string()) for name in names]

    def commit(self, comp):
        """If all the fields are valid, answer the modified fields

        In:
          - ``comp`` -- this component
        """
        if not any(name.error for name in self.names):
            comp.answer([name() for name in self.names])

@presentation.render_for(NamesEditor)
def render(self, h, comp, *args):
    h.head.css_url('form.css')

    with h.form:
        for name in self.names:
            with h.div:
                h << 'Name: '
                h << h.input(value=name()).action(name).error(name.error)

        h << h.input(type='submit', value='Changer').action(lambda: self.commit(comp))
        h << ' '
        h << h.input(type='submit', value='Annuler').action(comp.answer)

    return h.root

def modify_rows(table, selected_rows):
    """Edit the field ``name`` of the selected row

    In:
      - ``table`` -- the table widget component
      - ``selected_rows`` -- the selected rows
    """
    # Create a component to edit the field ``name`` (field #1) of the selected
    # rows, that temporary replace the table widget
    news = table.call(component.Component(NamesEditor([row[1] for row in selected_rows])))

    if news is None:
        # The modification was canceled
        return

    # Modification made, replace the ``name`` fields of the selected rows
    for (row, new) in zip(selected_rows, news):
        row[1] = new

def reset_rows(table, selected_rows):
    """Reset the field ``name`` of the selected rows

    In:
      - ``table`` -- the table widget component
      - ``selected_rows`` -- the selected rows
    """
    for row in selected_rows:
        row[1] = 'Default value'

def example4():
    rows = [[2, 'a'], [3, 'b'], [1, 'c']]
    headers = ('id', 'name')
    return widgets.SelectionTable(
                                    rows,
                                    headers, sortable_headers=headers,
                                    colors=('lightblue', 'white'),
                                    # List of the callbacks
                                    edit=(('Modifier', modify_rows), ('Reset', reset_rows))
                                   )

examples += ("Grid data with multiple actions", example4)
