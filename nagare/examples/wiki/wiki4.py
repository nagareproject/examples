#--
# Copyright (c) 2008-2012 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
#--

"""A Wiki component is added that manage the navigation into the pages
"""

from __future__ import with_statement

import re
import docutils.core

from nagare import component, presentation, var

from wikidata import PageData

# ---------------------------------------------------------------------------

wikiwords = re.compile(r'\b([A-Z]\w+[A-Z]+\w+)')

class Page(object):
    def __init__(self, title):
        self.title = title

    def edit(self, comp):
        content = comp.call(PageEditor(self))
        
        if content is not None:
            page = PageData.get_by(pagename=self.title)
            page.data = content
        
@presentation.render_for(Page)
def render(self, h, comp, *args):
    page = PageData.get_by(pagename=self.title)

    content = docutils.core.publish_parts(page.data, writer_name='html')['html_body']
    content = wikiwords.sub(r'<wiki>\1</wiki>', content)
    html = h.parse_htmlstring(content, fragment=True)[0]

    for node in html.getiterator():
        if node.tag == 'wiki':
            a = h.a(node.text).action(lambda title=unicode(node.text): comp.answer(title))
            node.replace(a)

    return (html, h.a('Edit this page').action(lambda: self.edit(comp)))

# ---------------------------------------------------------------------------

class PageEditor(object):
    def __init__(self, page):
        self.page = page
        
@presentation.render_for(PageEditor)
def render(self, h, comp, *args):
    content = var.Var()

    page = PageData.get_by(pagename=self.page.title)
    
    with h.form:
        with h.textarea(rows='10', cols='40').action(content):
            h << page.data
        h << h.br
        h << h.input(type='submit', value='Save').action(lambda: comp.answer(content()))
        h << ' '
        h << h.input(type='submit', value='Cancel').action(comp.answer)
                                                             
    return h.root

# ---------------------------------------------------------------------------

class Wiki(object):
    """Wiki component. Into the components graph, it'sthe parent of the
    displayed pages.
    """
    def __init__(self):
        # The ``content`` contains the page component currently displayed
        self.content = component.Component(None)
        # A page answers the WikiWord clicked. Bind the answer to the ``goto()``
        # method
        self.content.on_answer(self.goto)
        
        # The first displayed page is the ``FrontPage`` page
        self.goto(u'FrontPage')

    def goto(self, title):
        """Navigate to an other page
        
        In:
          - ``title`` -- title of the new page to display
        """
        # Retrieve the new page data from the database
        page = PageData.get_by(pagename=title)
        if page is None:
            # The new page doesn't exist, create it in database
            PageData(pagename=title, data='')
        
        # Permanently replace, into the component graph, the currently
        # displayed page by the new one
        self.content.becomes(Page(title))
        
@presentation.render_for(Wiki)
def render(self, h, *args):
    h.head.css('main_css', '''
    .document:first-letter { font-size:2em }
    ''')
    
    return self.content

# ---------------------------------------------------------------------------

app = Wiki
