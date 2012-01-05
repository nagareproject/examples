#--
# Copyright (c) 2008-2012 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
#--

"""Validations of the form fields added"""

from __future__ import with_statement

from nagare import presentation, component, editor, validator

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


class PhotoCreator(editor.Editor):
    def __init__(self):
        self.title = editor.Property(None)
        self.img = editor.Property(None)

        # The validation functions are added:
        #
        #   - the title must be a not empty string
        #   - a image must be uploaded
        self.title.validate(lambda t: validator.to_string(t).not_empty().to_string())
        self.img.validate(self.validate_img)

    def validate_img(self, img):
        if isinstance(img, basestring):
            raise ValueError, 'Image not provided'
        return img.file.read()

    def commit(self, comp):
        """The form is validated if the ``title`` and ``img`` property are valid
        (haven't a value to their ``error`` attribute)"""
        if self.is_validated(('title', 'img')):
            comp.answer((self.title(), self.img.value))

@presentation.render_for(PhotoCreator)
def render(self, h, comp, *args):
    with h.form:
        with h.table(border=0):
            with h.tr:
                # Call the `error()` method on the field to highlight them if
                # there are validation errors
                h << h.td('Title') << h.td(':') << h.td(h.input.action(self.title).error(self.title.error))

            with h.tr:
                h << h.td('Image') << h.td(':') << h.td(h.input(type='file').action(self.img).error(self.img.error))

            with h.tr:
                h << h.td() << h.td()
                with h.td:
                    h << h.input(type='submit', value='Add', id='submitbutton').action(lambda: self.commit(comp))
                    h << ' '
                    h << h.input(type='submit', value='Cancel', id='submitbutton').action(comp.answer)

    return h.root

# ---------------------------------------------------------------------------

class Gallery(object):
    def __init__(self, name):
        self.name = name

    def add_photo(self, comp):
        r = comp.call(PhotoCreator())
        if r is not None:
            (title, img) = r

            gallery = GalleryData.get_by(name=self.name)
            gallery.photos.append(PhotoData(title=title, img=img, thumbnail=img))

@presentation.render_for(Gallery)
def render(self, h, comp, *args):
    with h.div:
        h << h.h1('Gallery: ', self.name)
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
