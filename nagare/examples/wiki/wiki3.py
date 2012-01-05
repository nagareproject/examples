#--
# Copyright (c) 2008-2012 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
#--

"""The default view for a Page will now format its ReStructuredText
content in HTML and activate the WikiWord. NOTE: at this stage, clicking
on a WikiWord will raise an error.
"""

from __future__ import with_statement

import re               # To detect the WikiWords
import docutils.core    # To translate the ReST in HTML

from nagare import presentation, var

from wikidata import PageData

# ---------------------------------------------------------------------------

# WikiWords regular expression
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

    # Translate the content in ``page.data`` to HTML
    content = docutils.core.publish_parts(page.data, writer_name='html')['html_body']
    
    # For each WikiWords found, create a pseudo tag '<wiki>WikiWord</<wiki>'
    content = wikiwords.sub(r'<wiki>\1</wiki>', content)
    
    # Parse the HTML into a elements tree
    html = h.parse_htmlstring(content, fragment=True)[0]

    # Found the '<wiki>' elements into the tree and transform them into active links
    for node in html.getiterator():
        if node.tag == 'wiki':
            # Clicking on a WikiWord will answer the WikiWord unicode string
            a = h.a(node.text).action(lambda title=unicode(node.text): comp.answer(title))
            # Replace the node
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

app = lambda: Page(u'FrontPage')
