#--
# Copyright (c) 2008-2011 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
#--

from __future__ import with_statement

from nagare import presentation, editor
from lxml.html import clean

class Html:
    def __init__(self):
        self.content = ''

@presentation.render_for(Html)
def default_view(self, h, comp, *args):
    with h.div:
        if self.content:
            h << h.parse_htmlstring(self.content)

        h << h.a('Edit HTML').action(lambda: comp.call(HTMLEditor(self)))

    return h.root


def to_valid_html(value, msg="Not a valid html fragment"):
    try:
        return clean.Cleaner().clean_html(value)
    except:
        raise ValueError(msg)


class HTMLEditor(editor.Editor):
    fields = ('content', )

    def __init__(self, target):
        super(HTMLEditor, self).__init__(target, self.fields)
        self.content.validate(to_valid_html)

    def commit(self, comp):
        if super(HTMLEditor, self).commit(self.fields):
            comp.answer()

@presentation.render_for(HTMLEditor)
def default_view(self, h, comp, *args):
    with h.form:
        h << h.label('HTML source code')
        h << h.textarea(self.content, rows=15, cols=30).action(self.content).error(self.content.error)
        h << h.input(type='submit', value='Save').action(lambda: self.commit(comp))
        h << ' '
        h << h.input(type='submit', value='Cancel').action(comp.answer)

    return h.root

# -----------------------------------------------------------------------------

hl_lines = (
    range(3, 45),
    (
        (4,),
        '<p>A <code>HtmlWidget</code> is defined</p>'
        '<p>Its default view displays its HTML content</p>',
        range(4, 16)
    ),

    (
        (30, 39),
        '<p>Use of the Call/Answer mechanism: a <code>HtmlWidget</code> objects '
        'calls an <code>HTMLEditor</code></p>'
        '<p>When the `save` button is clicked, the <code>content</code> is changed, '
        'the editor answers and the <code>HtmlWidget</code> is rendered back</p>',
        [14, 30, 31, 32, 39]
    ),

    (
        (14, 41),
        '<p>Use of the Call/Answer mechanism: a <code>HtmlWidget</code> objects'
        'calls an <code>HTMLEditor</code></p>'
        '<p>When the `cancel` is clicked the editor answers and the '
        '<code>HtmlWidget</code> is rendered back',
        [14, 41]
    ),

    (
        (17, 28, 38),
        '<p><code>to_valid_html()</code> is a dedicated form field validator</p>'
        '<p>A validation method is associated to a Property object through its '
        '<code>validate()</code> method</p>',
        range(17, 22)+[28, 38]
    ),

    (
        (23,),
        '<p>Definition of a Nagare Editor</p>'
        '<p>Its default view is a form</p>'
        '<p><code>target</code> attribute is the edited <code>HtmlWidget</code> object</p>',
        range(23, 44)
    )
)
