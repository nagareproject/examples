#--
# Copyright (c) 2008-2012 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
#--

"""Example to demonstrate the use of asynchronous rendering of
components in a portal-like container
"""

from __future__ import with_statement

from nagare import component, presentation, ajax

from nagare.examples.wiki import wiki9
from nagare.examples.gallery import gallery7
from nagare.examples.jewels import Jewels
from nagare.examples.portal import html, tictactoe, counter, calculator
from nagare.examples.portal.source_viewer import SourceViewer

class Portal(object):
    """The ``Portal`` object is only a container"""

    def __init__(self):
        """Each components to display is simply an attribute"""
        self.calc = component.Component(calculator.Calculator())
        self.counter = component.Component(counter.Counter())
        self.tictactoe = component.Component(tictactoe.Task())
        self.wiki = component.Component(wiki9.app())
        self.jewels = component.Component(Jewels(10, 10))
        self.gallery = component.Component(gallery7.app())
        self.html = component.Component(html.Html())

@presentation.render_for(Portal)
def render(self, h, comp, *args):
    """The portal view uses YUI to display a portal-like structure with
    drag and drop aware portlets
    """
    h.head.javascript_url(ajax.YUI_INTERNAL_PREFIX + '/yahoo-dom-event/yahoo-dom-event.js')
    h.head.javascript_url(ajax.YUI_INTERNAL_PREFIX + '/dragdrop/dragdrop-min.js')

    h.head.css_url('portal.css')
    h.head.javascript_url('portal.js')

    with h.div(id='portal', class_='fixed_width'):

        # Each column must be a <div> with the class 'portlet_column'
        with h.div(class_='portlet_column'):
            # Each portlet must be a <div> with the class 'portlet'
            with h.div(class_='portlet about'):
                # Each D&D portlet handle must be a <div> with the class 'portlet_handle'
                h << h.span('Do you know?', class_='portlet_handle about_handle')

                with h.div(class_='portlet_content'):
                    h << h.p('Any Nagare component can be embedded into this portal, without any code modification!')
                    h << h.p('You can drag and drop the components')
                    h << h.p('Follow the "Click for details" link to dive into the code')

            with h.div(class_='portlet'):
                h << h.div('HTML', class_='portlet_handle')

                with h.div(class_='portlet_content'):
                    h << h.div('Add any HTML content', class_='portlet_comment')

                    # Each portlet is rendered asynchronously
                    h << h.div(self.html.render(h.AsyncRenderer()), class_='html')

                    h << h.a('Click for details', class_='source_link').action(lambda: comp.answer((self.html, html)))

            with h.div(class_='portlet'):
                h << h.div('Jewels', class_='portlet_handle')

                with h.div(class_='portlet_content'):
                    h << h.div('Click on a group of 2 or more jewels of the same color to make it disappear', class_='portlet_comment')

                    h.head.css_url('jewels.css')
                    h << self.jewels.render(h.AsyncRenderer())

            h << h.div(class_='drop_zone')

        with h.div(class_='portlet_column'):
            with h.div(class_='portlet'):
                h << h.div('TicTacToe', class_='portlet_handle')

                with h.div(class_='portlet_content'):
                    h << h.div('Enter the 2 players names then play', class_='portlet_comment')
                    h << self.tictactoe.render(h.AsyncRenderer())

                    h << h.a('Click for details', class_='source_link').action(lambda: comp.answer((self.tictactoe, tictactoe)))

            with h.div(class_='portlet'):
                h << h.div('Counter', class_='portlet_handle')
                with h.div(class_='portlet_content'):
                    h << h.div(self.counter.render(h.AsyncRenderer()), class_='comp')

                    h << h.a('Click for details', class_='source_link').action(lambda: comp.answer((self.counter, counter)))

            with h.div(class_='portlet'):
                h << h.div('Wiki', class_='portlet_handle')

                with h.div(class_='portlet_content'):
                    h << self.wiki.render(h.AsyncRenderer())

                    h << h.a('Wiki tutorial', class_='source_link', href='http://www.nagare.org/wiki')

            h << h.div(class_='drop_zone')

        with h.div(class_='portlet_column'):
            with h.div(class_='portlet'):
                h << h.div('RPN Calculator', class_='portlet_handle')

                with h.div(class_='portlet_content'):
                    with h.div(class_='portlet_comment'):
                        h << h.p('This is a RPN calculator')
                        h << h.p(u'Try: 3 \N{WHITE RIGHT-POINTING POINTER} 4 \N{MULTIPLICATION X}')

                    h << h.div(self.calc.render(h.AsyncRenderer()), class_='comp')

                    h << h.a('Click for details', class_='source_link').action(lambda: comp.answer((self.calc, calculator)))

            with h.div(class_='portlet'):
                h << h.div('Photos gallery', class_='portlet_handle')

                with h.div(class_='portlet_content'):
                    h << h.div('Upload pictures', class_='portlet_comment')
                    h << self.gallery.render(h.AsyncRenderer())
                    h << h.p(style='clear: both')

            h << h.div(class_='drop_zone')

    # Initialize the portal
    h << h.script('init_portal()', type='text/javascript')

    return h.root


class App(object):
    def __init__(self):
        self.portal = component.Component(Portal())
        self.source = component.Component(None)

        self.portal.on_answer(lambda args: self.source.call(SourceViewer(*args)))

@presentation.render_for(App)
def render(self, h, comp, *args):
    h.head << h.head.title('Demonstration portal')
    h.head.css_url('/static/nagare/application.css')

    with h.body:
        if self.source():
            h << { 'style' : 'overflow: hidden' }
            h << h.div(id='overlay1')
            h << h.div(self.source, id='overlay2')

        with h.div(id='body'):
            h << h.a(h.img(src='/static/nagare/img/logo_small.png'), id='logo', href='http://www.nagare.org/', title='Nagare home')

            with h.div(id='content'):
                h << h.div('Demonstrations portal', id='title')

                h << h.div(self.portal, id='main')

    return h.root

# ---------------------------------------------------------------------------

app = App
