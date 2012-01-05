#--
# Copyright (c) 2008-2012 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
#--

"""Adding a second view to the Page and PageEditor component, displaying
meta data about the current page and action. 
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

@presentation.render_for(Page, model='meta')
def render(self, h, comp, *args):
    """Second view, called ``meta``, for the Page component
    
    Display:
    
      - the current action : 'Viewing'
      - the current page title
      - a link to return to the 'FrontPage' page
    """
    return ('Viewing ', h.b(self.title), h.br, h.br,
            'You can return to the ', h.a('FrontPage').action(lambda: comp.becomes(Page(u'FrontPage'))))

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

@presentation.render_for(PageEditor, model='meta')
def render(self, h, *args):
    """Second view, called ``meta``, for the PageEditor component
    
    Display:
    
      - the current action : 'Editing'
      - the title of the current edited page
    """    
    return ('Editing ', h.b(self.page.title))

# ---------------------------------------------------------------------------

class Wiki(object):
    def __init__(self):
        self.content = component.Component(None)
        self.content.on_answer(self.goto)

        self.goto(u'FrontPage')

    def goto(self, title):
        page = PageData.get_by(pagename=title)
        if page is None:
            PageData(pagename=title, data='')

        self.content.becomes(Page(title))

@presentation.render_for(Wiki)
def render(self, h, *args):
    h.head.css('main_css', '''
    .document:first-letter { font-size:2em }
    .meta { float:right; width: 10em; border: 1px dashed gray;padding: 1em; margin: 1em; }
    ''')

    return (
             # The following div display the 'meta' view of the current
             # ``self.content`` component. It can be a Page component or
             # a PageEditor component. We don't care because both has a
             # ``meta`` view.
             h.div(self.content.render(h, model='meta'), class_='meta'),
             self.content,
            )

# ---------------------------------------------------------------------------

app = Wiki
