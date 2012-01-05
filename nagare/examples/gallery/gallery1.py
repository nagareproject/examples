#--
# Copyright (c) 2008-2012 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
#--

"""A Photo component is defined that can read its image, thumbnail and
title data from the database and display them
"""
from __future__ import with_statement

from nagare import presentation, component

from gallerydata import *

# ---------------------------------------------------------------------------

class Photo(object):
    """A Photo
    
    Its ``id`` is unique and is used to fetch the data from the database
    """
    def __init__(self, id):
        self.id = id

    @property
    def title(self):
        """Return the title of the photo"""
        return PhotoData.get(self.id).title

    def img(self):
        """Return the image data"""
        return str(PhotoData.get(self.id).img)

    def thumbnail(self):
        """Return the thumbnail data"""
        return str(PhotoData.get(self.id).thumbnail)

@presentation.render_for(Photo)
def render(self, h, *args):
    """The default view of a Photo displays it as a thumbnail with its title
    and its size"""

    with h.div:
        h << h.img(width='200').action(self.thumbnail)
        h << h.br
        h << self.title
        h << h.i(' (%d octets)' % len(self.img()))

    return h.root

# ---------------------------------------------------------------------------

# Display the first photo
app = lambda: Photo(1)
