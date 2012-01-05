#--
# Copyright (c) 2008-2012 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
#--

"""Dynamic generation of an image data

An action can be associated to an ``<img>` tag. This action must return
the image data.
"""

import urllib

from nagare import presentation

class Image(object):
    """A proxy image object to an image on the net"""
    def __init__(self, title, url):
        """Initialization
        
        In:
          - ``title`` -- title of the image
          - ``url`` -- url where to fetch the image data
        """
        self.title = title
        self.url = url
        
    def send_image(self):
        """Read the image data
        
        In:
          - ``h`` -- the current renderer

        Return:
          - the image data
        """
        return urllib.urlopen(self.url).read()

@presentation.render_for(Image)
def render(self, h, *args):
    # An action can be associated to a ``<img>`` tag
    return (h.h1(self.title), h.img.action(self.send_image))

app = lambda: Image('Hello world !', 'http://www.google.fr/intl/fr_fr/images/logo.gif')
