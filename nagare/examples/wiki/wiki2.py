#--
# Copyright (c) 2008-2012 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
#--

"""A PageEditor component is added to edit the content of a page
"""

from __future__ import with_statement

from nagare import presentation, var

from wikidata import PageData

# ---------------------------------------------------------------------------

class Page(object):
    def __init__(self, title):
        self.title = title

    def edit(self, comp):
        """Edit the content of this page:
        
           1. a page editor is created
           2. the page editor temporary replace the page in the component graph
           3. it will return (and restore the page) with the new content of the
              page

        In:
          - ``comp`` -- this component
        """
        # A ``PageEditor`` object is created for ``self``
        # It temporary replaces the current component (the page displayed)
        content = comp.call(PageEditor(self))
        
        # ``content`` is the new content for the page
        # or ``None`` if the user canceled the modification
        if content is not None:
            # Retrieve the database object
            page = PageData.get_by(pagename=self.title)
            # Change the content
            page.data = content
        
@presentation.render_for(Page)
def render(self, h, comp, *args):
    page = PageData.get_by(pagename=self.title)
    
    with h.div:    
        h << h.pre(page.data)

        # This link is added to every page displayed, to be able to edit it
        h << h.a('Edit this page').action(lambda: self.edit(comp))

    return h.root

# ---------------------------------------------------------------------------

class PageEditor(object):
    """An object dedicated to the edition of a page content
    """
    def __init__(self, page):
        """Initialization
        
        In:
          - ``page`` -- the page to edit
        """
        self.page = page
        
@presentation.render_for(PageEditor)
def render(self, h, comp, *args):
    content = var.Var() # Local functional variable that will keep the new page content
    
    # Retrieve the database object
    page = PageData.get_by(pagename=self.page.title)
    
    with h.form:
        with h.textarea(rows='10', cols='40').action(content): # Calling ``content`` with a value set its
            h << page.data
        h << h.br
        # Clicking on 'Save', will answer the new content
        h << h.input(type='submit', value='Save').action(lambda: comp.answer(content()))
        h << ' '
        # Clicking on 'Cancel', will answer ``None``
        h << h.input(type='submit', value='Cancel').action(comp.answer)
                                                             
    return h.root

# ---------------------------------------------------------------------------

app = lambda: Page(u'FrontPage')
