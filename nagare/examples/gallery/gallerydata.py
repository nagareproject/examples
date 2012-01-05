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

class PhotoData(Entity):
    title = Field(Unicode(100))
    img = Field(BLOB)
    thumbnail = Field(BLOB)
    
    belongs_to('gallery', of_kind='GalleryData')

        
class GalleryData(Entity):
    name = Field(Unicode(40))
   
    has_many('photos', of_kind='PhotoData')

# ---------------------------------------------------------------------------

def populate1():
    import os

    gallery = GalleryData(name=u'MyGallery')
  
    f = file(os.path.join(os.path.dirname(__file__), 'dragon.jpg'))
    img = f.read()
    f.close()
        
    gallery.photos.append(PhotoData(title=u'Dragon', img=img, thumbnail=img))

def populate2():
    GalleryData(name=u'MyGallery')
