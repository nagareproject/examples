#--
# Copyright (c) 2008, Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
#--

"""Basic examples of components, multiple views and synchronous/asynchronous
callbacks
"""

from __future__ import with_statement

from nagare import component, presentation, var
from nagare.namespaces import xhtml

examples = ()

# ---------------------------------------------------------------------

# This example:
#
# - shows how to add multiples web views on a Python object
# - shows how to associate methods actions to HTML elements 

class Counter1:
    """A simple counter with ``increase`` and ``decrease`` logics
    """
    def __init__(self, start=0):
        self.v = start

    def increase(self):
        self.v += 1

    def decrease(self):
        self.v -= 1

@presentation.render_for(Counter1)
def render(self, h, comp, *args):
    """This view is wrote in "functional HTML"
    
    In:
      - ``h`` -- the renderer
      - ``comp`` -- the component
      
    Return:
      - the view of the referenced object
    """
    return (
             'Value: ', self.v, h.br,
             h.a('++').action(self.increase),
             '|',
             h.a('--').action(self.decrease),
             h.hr,
             h.a('Freeze it !').action(lambda: comp.becomes(self, model='freeze'))
           )

@presentation.render_for(Counter1, model='with')
def render(self, h, comp, *args):
    """Same view but written in "imperative HTML"
    
    In:
      - ``h`` -- the renderer
      - ``comp`` -- the component
      
    Return:
      - the view of the referenced object
    """    
    with h.div:
        h << 'Value: ' << self.v << h.br
        h << h.a('++').action(self.increase) << '|' << h.a('--').action(self.decrease)

        h << h.hr

        h << h.a('Freeze it !').action(lambda: comp.becomes(self, model='freeze'))

    return h.root

@presentation.render_for(Counter1, model='freeze')
def render(self, h, *args):
    """An other view, displaying only the counter value, without any actions
    possible
    
    In:
      - ``h`` -- the renderer
      - ``comp`` -- the component
      
    Return:
      - the view of the referenced object
    """    
    return h.h2(self.v)

examples += ('Multiple views and methods callbacks', Counter1)

# ---------------------------------------------------------------------------

# This example:
#
# - shows how to add multiples web views on a Python object
# - shows how to associate lambdas actions to HTML elements 

from nagare.var import Var

class Counter2:
    """The value is kept into a functional variable. Easier to work with
    into lambdas expressions.
    """
    def __init__(self, start=0):
        self.v = Var(start)

@presentation.render_for(Counter2)
def render(self, h, comp, *args):
    """View with lambdas as actions
    
    In:
      - ``h`` -- the renderer
      - ``comp`` -- the component
      
    Return:
      - the view of the referenced object
    """    
    return (
             'Value: ', self.v, h.br,
             h.a('++').action(lambda: self.v(self.v()+1)),
             '|',
             h.a('--').action(lambda: self.v(self.v()-1)),
             h.hr,
             h.a('Freeze it !').action(lambda: comp.becomes(self, model='freeze')),
           )

@presentation.render_for(Counter2, 'freeze')
def render(self, h, *args):
    """An other view, displaying only the counter value, without any actions
    possible
    
    In:
      - ``h`` -- the renderer
      - ``comp`` -- the component
      
    Return:
      - the view of the referenced object
    """    
    return h.h2(self.v)

examples += ('Multiple views and lambdas callbacks', Counter2)

# ---------------------------------------------------------------------

# This example:
#
# - shows how to render a component with an asynchronous renderer
# - shows that the code of a component doesn't need to be modified to
#   become asynchronous

class App:
    def __init__(self):
        # Incremented each time the page is fully re-generated
        self.nb_display = 0

        # 2 different components of the same type
        self.counter1 = component.Component(Counter2())
        self.counter2 = component.Component(Counter2())

@presentation.render_for(App)
def render(self, h, *args):
    self.nb_display += 1

    with h.div:
        h << 'Nb displays: ' << self.nb_display << h.br << h.br

        with h.table(width='100%'):
            with h.tr:
                h << h.td(h.u('Synchronous'))
                h << h.td(h.u('Asynchronous'))
                
            with h.tr:
                # The ``counter1`` component is rendered with a standard HTML renderer
                h << h.td(self.counter1)

                # The ``counter2`` component is rendered with an asynchronous HTML renderer
                h << h.td(self.counter2.render(xhtml.AsyncRenderer(h)))

    return h.root

examples += ('Automatic use of asynchronous requests/updates', App) 

# ---------------------------------------------------------------------

# This example:
#
# - shows how to explicitly use a ``ajax.Update`` callback to change a HTML
#   element asynchronously (using its id)

from nagare import ajax

class Counter4:
    def __init__(self, start=0):
        self.v = start

    def increase(self):
        self.v += 1

    def decrease(self):
        self.v -= 1

@presentation.render_for(Counter4)
def render(self, h, *args):
    return (
            # HTML element to update
            h.div('0', id='value'),
            
            # ``ajax.Update`` object that:
            #
            #   - calls ``self.decrease`` as action
            #   - calls ``lambda h: str(self.v)`` to render the view
            #   - updates the HTML element with the id ``value`` on the client
            h.a('--').action(ajax.Update(lambda h: str(self.v), self.decrease, 'value')),
            ' | ',
            
            # ``ajax.Update`` object that:
            #
            #   - calls ``self.increase`` as action
            #   - calls ``lambda h: str(self.v)`` to render the view
            #   - updates the HTML element with the id ``value`` on the client
            h.a('++').action(ajax.Update(lambda h: str(self.v), self.increase, 'value')),
           )

examples += ('Asynchronous update of a HTML element', Counter4)

# ---------------------------------------------------------------------

# This example:
#
# - shows how to explicitly use a ``ajax.Update`` callback to change a HTML
#   element asynchronously

@presentation.render_for(Counter4, model='without_id')
def render(self, h, *args):
    # HTML element to update
    div = h.div(0)

    return (
            div,

            # ``ajax.Update`` object that:
            #
            #   - calls ``self.decrease`` as action
            #   - calls ``lambda h: str(self.v)`` to render the view
            #   - updates the given HTML element
            h.a('--').action(ajax.Update(lambda h: str(self.v), self.decrease, div)),
            ' | ',
            
            # ``ajax.Update`` object that:
            #
            #   - calls ``self.increase`` as action
            #   - calls ``lambda h: str(self.v)`` to render the view
            #   - updates the given HTML element
            h.a('++').action(ajax.Update(lambda h: str(self.v), self.increase, div)),
           )

examples += ('Asynchronous update of a HTML element', lambda: component.Component(Counter4(), model='without_id'))
