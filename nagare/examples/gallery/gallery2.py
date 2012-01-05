#--
# Copyright (c) 2008-2012 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
#--

"""A Gallery component is defined that manage a set of Photos
"""

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

@presentation.render_for(Photo, model='thumbnail')
def render(self, h, *args):
    """View renamed to ``thumbnail``"""
    with h.div:
        h << h.img(width='200').action(self.thumbnail)
        h << h.br
        h << self.title
        h << h.i(' (%d octets)' % len(self.img()))

    return h.root


class Gallery(object):
    def __init__(self, name):
        """A gallery has a name"""
        self.name = name

@presentation.render_for(Gallery)
def render(self, h, *args):
    """The default view of a Gallery displays the list of the Photos"""
    
    with h.div:
        h << h.h1('Gallery: ', self.name)
        h << h.br

        with h.ul:
            # Use the database relation to get all the photos of this
            # gallery
            for p in GalleryData.get_by(name=self.name).photos:
                # Create a Photo object with the id of the photo
                # then make it a component to display ir
                photo = component.Component(Photo(p.id))

                # Render the ``thumbnail`` view of the Photo component
                h << h.li(photo.render(h, model='thumbnail'))

    return h.root

# ---------------------------------------------------------------------------

app = lambda: Gallery(u'MyGallery')
