#--
# Copyright (c) 2008, 2009, 2010 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
#--

from nagare.database import session

from sqlalchemy import MetaData, Table, Column, Unicode, BLOB, ForeignKey, Integer
from sqlalchemy.orm import mapper, relation, deferred

from nagare.examples.gallery.gallery8 import Photo, Gallery

__metadata__ = MetaData()

photo_table = Table(
                    'photo', __metadata__,
                    Column('title', Unicode(100), primary_key=True),
                    Column('img', BLOB),
                    Column('thumbnail', BLOB),
                    Column('size', Integer),
                    
                    Column('gallery_id', Unicode(40), ForeignKey('gallery.name'))
                   )

gallery_table = Table(
                     'gallery', __metadata__,
                     Column('name', Unicode(40), primary_key=True)
                    )

mapper(Photo, photo_table, properties={ 'img' : deferred(photo_table.c.img) })
mapper(Gallery, gallery_table, properties={ 'photos' : relation(Photo, backref='gallery') })

# ---------------------------------------------------------------------------

def populate():
    session.add(Gallery(name=u'MyGallery'))
