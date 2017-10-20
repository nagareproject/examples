# --
# Copyright (c) 2008-2017 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
# --

"""A Gallery component is defined that manage a set of Photos
"""
from nagare import presentation, component

from gallerydata import PhotoData, GalleryData


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
        self.photos = []

    def get_photos(self):
        """Use the database relation to get all the photos of this gallery

        Return:
           ``Photo()`` components
        """
        photos = GalleryData.get_by(name=self.name).photos

        # Create a Photo object with the id of the photo then make it a component
        self.photos = [component.Component(Photo(p.id)) for p in photos]
        return self.photos


@presentation.render_for(Gallery)
def render(self, h, *args):
    """The default view of a Gallery displays the list of the Photos"""

    with h.div:
        h << h.h1('Gallery: ', self.name)
        h << h.br

        with h.ul:
            # Render the ``thumbnail`` view of the Photo component
            h << h.li(photo.render(h, model='thumbnail') for photo in self.get_photos())

    return h.root


# ---------------------------------------------------------------------------

def app():
    return Gallery(u'MyGallery')
