#--
# Copyright (c) 2008-2012 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
#--

"""Actions added to navigate between the thumbnail view and the full view
of the Photos"""

from __future__ import with_statement

from nagare import presentation, component

from gallerydata import *

# ---------------------------------------------------------------------------

class Photo(object):
    def __init__(self, id):
        self.id = id

    @property
    def title(self):
        return PhotoData.get(self.id).title

    def img(self):
        return str(PhotoData.get(self.id).img)

    def thumbnail(self):
        return str(PhotoData.get(self.id).thumbnail)

@presentation.render_for(Photo)
def render(self, h, comp, *args):
    """The default view of a Photo displays the whole image"""
    
    # The image
    img = h.img.action(self.img)
    
    # On a click, the image answers ``None``
    return h.a(img).action(comp.answer)

@presentation.render_for(Photo, model='thumbnail')
def render(self, h, comp, *args):
    with h.div:
        h << h.img(width='200').action(self.thumbnail)
        h << h.br
        
        # On a click on its title, the Photo object answers itself
        h << h.a(self.title).action(lambda: comp.answer(self))
        h << h.i(' (%d octets)' % len(self.img()))

    return h.root


class Gallery(object):
    def __init__(self, name):
        self.name = name

@presentation.render_for(Gallery)
def render(self, h, comp, *args):
    with h.div:
        h << h.h1('Gallery: ', self.name)
        h << h.br

        with h.ul:
            for p in GalleryData.get_by(name=self.name).photos:
                photo = component.Component(Photo(p.id))
                
                # On a click on the title of a Photo, the Gallery temporary
                # changes itself by this Photo, displayed in its default view 
                photo.on_answer(comp.call)

                h << h.li(photo.render(h, model='thumbnail'))

    return h.root

# ---------------------------------------------------------------------------

app = lambda: Gallery(u'MyGallery')
