#--
# Copyright (c) 2008-2012 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
#--

"""A Page component is defined that can read its content from the database
and display it
"""
from __future__ import with_statement

from nagare import presentation
from nagare.var import Var

from nagare.examples.wiki.wikidata import PageData   # The database entities

# ---------------------------------------------------------------------------

class Page(object):
    """A wiki page
    
    Its title is unique. It will be also the WikiWord others pages will use
    to link to this page.
    
    ``title`` is used to fetch the data from the database
    """
    def __init__(self, title):
        """Initialization
        
        In:
          - ``title`` -- the WikiWord title of the page
        """
        self.title = title

@presentation.render_for(Page)
def render(self, h, *args):
    """Display the raw content of the page
    """
    page = PageData.get_by(pagename=self.title) # Fetch all the data from the database

    # Display the content in a ``<pre>`` tag
    with h.div:
        h << h.pre(page.data)

    return h.root

# ---------------------------------------------------------------------------

app = lambda: Page(u'FrontPage') # The factory creates the ``FrontPage`` page
