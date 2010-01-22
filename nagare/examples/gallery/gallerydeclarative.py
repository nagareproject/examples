#--
# Copyright (c) 2008, 2009, 2010 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
#--

#from nagare.database import session

from sqlalchemy import MetaData
from sqlalchemy.ext import declarative

__metadata__ = MetaData()
Entity = declarative.declarative_base(metadata=__metadata__)

# ---------------------------------------------------------------------------

def populate2():
    session.add(GalleryData(name=u'MyGallery'))
