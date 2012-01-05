#--
# Copyright (c) 2008-2012 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
#--

"""Form, to append a new photo to a gallery, added"""

from __future__ import with_statement

from nagare import presentation, component, editor

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
    img = h.img.action(self.img)
    return h.a(img).action(comp.answer)

@presentation.render_for(Photo, model='thumbnail')
def render(self, h, comp, *args):
    with h.div:
        h << h.img(width='200').action(self.thumbnail)
        h << h.br
        h << h.a(self.title).action(lambda: comp.answer(self))
        h << h.i(' (%d octets)' % len(self.img()))

    return h.root

# A PhotoCreator is defined, to download a new Photo
class PhotoCreator(editor.Editor):
    def __init__(self):
        """At this stage, we are using ``editor.Property`` but without
          validation functions"""
        self.title = editor.Property(None)
        self.img = editor.Property(None)

    def commit(self, comp):
        """After the submission of the form, the PhotoCreator answers the
           tuple (title of the photo, image data)"""
        comp.answer((self.title(), self.img.value.file.read()))

@presentation.render_for(PhotoCreator)
def render(self, h, comp, *args):
    """The default view of a PhotoCreator component is the upload form"""
    with h.form:
        with h.table(border=0):
            with h.tr:
                # The action on the "Title" field is to call ``self.title`` i.e
                # put the value of the field into the ``title`` property
                h << h.td('Title') << h.td(':') << h.td(h.input.action(self.title))

            with h.tr:
                # The action on the "Image" field is to call ``self.image`` i.e
                # put the value of the field into the ``image`` property
                h << h.td('Image') << h.td(':') << h.td(h.input(type='file').action(self.img))

            with h.tr:
                h << h.td << h.td
                with h.td:
                    # The action on the "Add" button is to call ``self.commit``, i.e
                    # answer the tuple (title of the photo, image data)
                    h << h.input(type='submit', value='Add').action(lambda: self.commit(comp))
                    
                    h << ' '
                    
                    # The action on the "Cancel" button is to call ``comp.answer``, i.e
                    # answer ``None``
                    h << h.input(type='submit', value='Cancel').action(comp.answer)

    return h.root

# ---------------------------------------------------------------------------

class Gallery(object):
    def __init__(self, name):
        self.name = name

    def add_photo(self, comp):
        """This method temporary replaces the Gallery component by a PhotoCreator
           component. Upon submission of a photo, the PhotoCreator answers with
           the title and the uploaded image"""
           
        # Change the Gallery by a PhotoCreator component
        r = comp.call(PhotoCreator())
        
        if r is not None:
            # If the user click on the the "Cancel" button, we receive ``None``
            # else we receive the title and the uploaded image
            (title, img) = r

            # Insert these data into the database
            gallery = GalleryData.get_by(name=self.name)
            gallery.photos.append(PhotoData(title=title, img=img, thumbnail=img))

@presentation.render_for(Gallery)
def render(self, h, comp, *args):
    with h.div:
        h << h.h1('Gallery: ', self.name)
        
        # In the default Gallery view, add a link to add a new photo
        h << h.a('Add photo').action(lambda: self.add_photo(comp))

        h << h.br

        with h.ul:
            for p in GalleryData.get_by(name=self.name).photos:
                photo = component.Component(Photo(p.id))
                photo.on_answer(comp.call)

                h << h.li(photo.render(h, model='thumbnail'))

    return h.root

# ---------------------------------------------------------------------------

app = lambda: Gallery(u'MyGallery')
