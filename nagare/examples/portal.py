#--
# Copyright (c) 2008, 2009, 2010 Net-ng.
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
from nagare.namespaces import xhtml

from nagare.examples import counter, calculator, tictactoe
from nagare.examples.wiki import wiki9
from nagare.examples.gallery import gallery7
from nagare.examples.jewels import Jewels

class Portal(object):
    """The ``Portal`` object is only a container"""

    def __init__(self):
        """Each components to display is simply an attribute"""
        self.calc = component.Component(calculator.Calculator())
        self.counter = component.Component(counter.Counter1())
        self.tictactoe = component.Component(tictactoe.Task())
        self.wiki = component.Component(wiki9.app())
        self.jewels = component.Component(Jewels(15, 10))
        self.gallery = component.Component(gallery7.app())


@presentation.render_for(Portal)
def render(self, h, *args):
    """The portal view uses YUI to display a portal-like structure with
    drag and drop aware portlets
    """
    h.head.javascript_url(ajax.YUI_EXTERNAL_PREFIX + '/yahoo-dom-event/yahoo-dom-event.js')
    h.head.javascript_url(ajax.YUI_EXTERNAL_PREFIX + '/dragdrop/dragdrop.js')
    h.head.javascript_url(ajax.YUI_EXTERNAL_PREFIX + '/dom/dom.js')

    h.head.javascript_url('portal.js')
    h.head.css_url('portal.css')

    h.head << h.head.title('Portal demonstration')

    with h.div(id='portal', class_='FixedWidth'):

        # Each column must be a <div> with the class 'portletColumn'
        with h.div(class_='portletColumn'):
            # Each portlet must be a <div> with the class 'portlet'
            with h.div(class_='portlet'):
                # Each D&D portlet handle must be a <div> with the class 'portletHandle'
                h << h.div('About', class_='portletHandle')
                with h.div:
                    h << h.p('This is a simple prototype of a dashboard that allows you to reorder containers much like iGoogle')
                    h << h.p('Select a container and drag it to another column.  As you do so, a marker appears between the place where to drop the element.')
                    h << h.p('Drag and drop is facilitated by the ', h.a('YUI Library.', href='http://developer.yahoo.com/yui/'))

            with h.div(class_='portlet'):
                h << h.div('Counter', class_='portletHandle')
                # Render the default asynchronous view of the component
                h << self.counter.render(xhtml.AsyncRenderer(h))

            with h.div(class_='portlet'):
                h << h.div('RPN Calculator', class_='portletHandle')
                h << self.calc.render(xhtml.AsyncRenderer(h))

        with h.div(class_='portletColumn'):
            with h.div(class_='portlet'):
                h << h.div('TicTacToe', class_='portletHandle')
                h << self.tictactoe.render(xhtml.AsyncRenderer(h))

            with h.div(class_='portlet'):
                h << h.div('Wiki', class_='portletHandle')
                h << self.wiki.render(xhtml.AsyncRenderer(h))
                h << h.p(style='clear: both')

            with h.div(class_='portlet'):
                h << h.div('Jewels', class_='portletHandle')

                h.head.css_url('jewels.css')
                h << h.div(self.jewels.render(xhtml.AsyncRenderer(h)), class_='jewels')

                h << h.p(style='clear: both')

        with h.div(class_='portletColumn'):
            with h.div(class_='portlet'):
                h << h.div('Photos gallery', class_='portletHandle')
                h << self.gallery.render(xhtml.AsyncRenderer(h))
                h << h.p(style='clear: both')

        # Initialize the portal
        h << h.script('portalInit("portal")', type='text/javascript')

    return h.root

# ---------------------------------------------------------------------------

app = Portal
