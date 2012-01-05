#--
# Copyright (c) 2008-2012 Net-ng.
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

from nagare import component, presentation

examples = ()

# ---------------------------------------------------------------------

# This example:
#
# - shows how to add multiples web views on a Python object
# - shows how to associate method actions to HTML elements

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
    """Same view but written in "imperative HTML"

    In:
      - ``h`` -- the renderer
      - ``comp`` -- the component

    Return:
      - the view of the referenced object
    """
    h.head.css_url('counter.css')

    with h.div(class_='counter'):
        h << h.div(self.v)

        with h.span:
            h << h.a(u'\N{MINUS SIGN}', title='decrease').action(self.decrease)

        with h.span:
            h << h.a('=', title='freeze').action(lambda: comp.becomes(self, model='freezed'))

        with h.span:
            h << h.a(u'\N{PLUS SIGN}', title='increase').action(self.increase)

    return h.root

@presentation.render_for(Counter1, model='freezed')
def render(self, h, *args):
    """An other view, displaying only the counter value, without any actions
    possible

    In:
      - ``h`` -- the renderer
      - ``comp`` -- the component

    Return:
      - the view of the referenced object
    """
    h.head.css_url('counter.css')

    with h.div(class_='counter'):
        h << h.div(self.v)

        with h.span:
            h << h.a(u'\N{MINUS SIGN}', class_='disabled')

        with h.span:
            h << h.a('=', class_='disabled')

        with h.span:
            h << h.a(u'\N{PLUS SIGN}', class_='disabled')

    return h.root

examples += ('Multiple views and methods callbacks', Counter1)

'''
@presentation.render_for(Counter1)
def render(self, h, comp, *args):
    """This view is written in "functional HTML"

    In:
      - ``h`` -- the renderer
      - ``comp`` -- the component

    Return:
      - the view of the referenced object
    """
    return (
             h.div('Value: ', self.v),
             h.a('++').action(self.increase),
             '|',
             h.a('--').action(self.decrease),
             h.hr,
             h.a('Freeze it !').action(lambda: comp.becomes(self, model='freeze'))
           )
'''

# ---------------------------------------------------------------------------

# This example:
#
# - shows how to add multiples web views on a Python object
# - shows how to associate lambda actions to HTML elements

from nagare.var import Var

class Counter2:
    """The value is kept into a functional variable. Easier to work with,
    into lambda expressions.
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
    h.head.css_url('counter.css')

    with h.div(class_='counter'):
        h << h.div(self.v)

        with h.span:
            h << h.a(u'\N{MINUS SIGN}', title='decrease').action(lambda: self.v(self.v()-1))

        with h.span:
            h << h.a('=', title='freeze').action(lambda: comp.becomes(self, model='freezed'))

        with h.span:
            h << h.a(u'\N{PLUS SIGN}', title='increase').action(lambda: self.v(self.v()+1))

    return h.root

@presentation.render_for(Counter2, model='freezed')
def render(self, h, *args):
    """An other view, displaying only the counter value, without any actions
    possible

    In:
      - ``h`` -- the renderer
      - ``comp`` -- the component

    Return:
      - the view of the referenced object
    """
    h.head.css_url('counter.css')

    with h.div(class_='counter'):
        h << h.div(self.v)

        with h.span:
            h << h.a(u'\N{MINUS SIGN}', class_='disabled')

        with h.span:
            h << h.a('=', class_='disabled')

        with h.span:
            h << h.a(u'\N{PLUS SIGN}', class_='disabled')

    return h.root

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
        self.counter1 = component.Component(Counter1())
        self.counter2 = component.Component(Counter1())

@presentation.render_for(App)
def render(self, h, *args):
    self.nb_display += 1

    with h.div:
        h << h.div('Full page generation: ', self.nb_display)

        with h.div(style='float: left; margin-top: 10px'):
            h << h.div('Synchronous', style='text-align: center')

            # The ``counter1`` component is rendered with a standard HTML renderer
            h << self.counter1

        with h.div(style='float: right; margin-top: 10px'):
            h << h.div('Asynchronous', style='text-align: center')

            # The ``counter2`` component is rendered with an asynchronous HTML renderer
            h << self.counter2.render(h.AsyncRenderer())

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
    h.head.css_url('counter.css')

    with h.div(class_='counter'):
        h << h.div(self.v, id='value')

        with h.span:
            h << h.a(u'\N{MINUS SIGN}', title='decrease').action(ajax.Update(lambda h: str(self.v), self.decrease, 'value'))

        with h.span:
            h << h.a('=', class_='disabled')

        with h.span:
            h << h.a(u'\N{PLUS SIGN}', title='increase').action(ajax.Update(lambda h: str(self.v), self.increase, 'value'))

    return h.root

examples += ('Asynchronous update of a HTML element', Counter4)

# ---------------------------------------------------------------------

# This example:
#
# - shows how to explicitly use a ``ajax.Update`` callback to change a HTML
#   element asynchronously

"""
@presentation.render_for(Counter4, model='without_id')
def render(self, h, *args):
    # HTML element to update
    div = h.div(0)

    return (
            div,

            # ``ajax.Update`` object that:
            #
            #   - calls ``self.increase`` as action
            #   - calls ``lambda h: str(self.v)`` to render the view
            #   - updates the given HTML element
            h.a('++').action(ajax.Update(lambda h: str(self.v), self.increase, div)),

            ' | ',

            # ``ajax.Update`` object that:
            #
            #   - calls ``self.decrease`` as action
            #   - calls ``lambda h: str(self.v)`` to render the view
            #   - updates the given HTML element
            h.a('--').action(ajax.Update(lambda h: str(self.v), self.decrease, div)),
           )
"""

@presentation.render_for(Counter4, model='without_id')
def render(self, h, *args):
    h.head.css_url('counter.css')

    with h.div(class_='counter'):
        div = h.div(self.v)

        h << div

        with h.span:
            h << h.a(u'\N{MINUS SIGN}', title='decrease').action(ajax.Update(lambda h: str(self.v), self.decrease, div))

        with h.span:
            h << h.a('=', class_='disabled')

        with h.span:
            h << h.a(u'\N{PLUS SIGN}', title='increase').action(ajax.Update(lambda h: str(self.v), self.increase, div))

    return h.root

class App2:
    def __init__(self):
        self.counter = component.Component(Counter4(), model='without_id')

@presentation.render_for(App2)
def render(self, h, *args):
    return self.counter.render(h)

examples += ('Asynchronous update of a HTML element', App2)
