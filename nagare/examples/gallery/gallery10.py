#--
# Copyright (c) 2008, 2009, 2010 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
#--

"""Adding significative URLs"""

from __future__ import with_statement

from nagare import presentation, component, editor, validator
from nagare.database import session, query

from elixir import *
from gallerydata2 import __metadata__
import thumb

class Photo(Entity):
    using_options(autoload=False)

    title = Field(Unicode(100))
    img = Field(BLOB)
    thumbnail = Field(BLOB)
    belongs_to('gallery', of_kind='Gallery')

@presentation.render_for(Photo)
def render(self, h, comp, *args):
    img = h.img.action(lambda h: str(self.img))
    return h.a(img).action(comp.answer)

@presentation.render_for(Photo, model='thumbnail')
def render(self, h, comp, *args):
    with h.div:
        h << h.img.action(lambda h: str(self.thumbnail))
        h << h.br
        h << h.a(self.title).action(lambda: comp.answer(self))
        h << h.i(' (%d octets)' % len(self.img))

    return h.root


class PhotoCreator(editor.Editor):
    def __init__(self):
        super(PhotoCreator, self).__init__(Photo(), ('title', 'img'))

        self.title.validate(lambda t: validator.to_string(t).not_empty().to_string())
        self.img.validate(self.validate_img)

    def validate_img(self, img):
        if isinstance(img, basestring):
            raise ValueError, 'Image not provided'
        return img.file.read()

    def commit(self, comp):
        if super(PhotoCreator, self).commit(('title', 'img')):
            photo = self.target

            photo.thumbnail = thumb.thumbnail(self.img.value)
            comp.answer(photo)

@presentation.render_for(PhotoCreator)
def render(self, h, comp, *args):
    with h.form:
        with h.table(border=0):
            with h.tr:
                h << h.td('Title') << h.td(':') << h.td(h.input.action(self.title).error(self.title.error))

            with h.tr:
                h << h.td('Image') << h.td(':') << h.td(h.input(type='file').action(self.img).error(self.img.error))

            with h.tr:
                h << h.td << h.td
                with h.td:
                    h << h.input(type='submit', value='Add').action(lambda: self.commit(comp))
                    h << ' '
                    h << h.input(type='submit', value='Cancel').action(comp.answer)

    return h.root

# ---------------------------------------------------------------------------

class Gallery(Entity):
    name = Field(Unicode(40))
    has_many('photos', of_kind='Photo')

    def __init__(self, name):
        self.name = name

    def add_photo(self, comp):
        photo = comp.call(PhotoCreator())
        if photo is not None:
            self.photos.append(photo)

@presentation.render_for(Gallery)
def render(self, h, comp, *args):
    h.head.css('gallery', '''
    ul.photo_list {
        list-style: none;
    }

    ul.photo_list li {
        display: block;
        float: left;
        border: 1px dashed gray;
        padding: 1em;
        margin: 1em;
    }
    ''')

    with h.div:
        h << h.h1('Gallery: ', self.name)
        h << h.a('Add photo', style='float: right').action(lambda: self.add_photo(comp))
        h << h.br

        with h.ul(class_='photo_list'):
            for photo in self.photos:
                # The url for a photo is its title
                photo = component.Component(photo, url=photo.title)
                photo.on_answer(comp.call)

                h << h.li(photo.render(h, model='thumbnail'))

    return h.root

# From a URL received, set the components
@presentation.init_for(Gallery, "len(url) == 1")
def init(self, url, comp, *args):
    # The URL received is the name of the photo
    photo = query(Photo).filter_by(title=url[0]).first()
    if not photo:
        # A photo with this name doesn't exist
        raise presentation.HTTPNotFound()
    
    # Temporary change the Gallery (the ``comp``) with the photo
    component.call_wrapper(lambda: comp.call(component.Component(photo)))

# ---------------------------------------------------------------------------

app = lambda: query(Gallery).filter_by(name=u'MyGallery').one()

def populate():
    session.add(Gallery(name=u'MyGallery'))
