#--
# Copyright (c) 2008-2012 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
#--

from elixir import *
from sqlalchemy import MetaData

__metadata__ = MetaData()

class PageData(Entity):
    pagename = Field(Unicode(40), primary_key=True)
    data = Field(Unicode(10*1024))
    creator = Field(Unicode(40))

# ---------------------------------------------------------------------------

def populate():
    page = PageData()
    page.pagename = u'FrontPage'
    page.data = u'Welcome to my *WikiWiki* !'
    page.creator = u'admin'
    
    page = PageData()
    page.pagename = u'WikiWiki'
    page.data = u'On this *WikiWiki*, the page contents can be ' \
                 'written in `Restructured Text <http://docutils.sourceforge.net/rst.html>`_'
    page.creator = u'john'
