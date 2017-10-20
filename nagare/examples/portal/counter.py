# --
# Copyright (c) 2008-2017 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
# --

from nagare import presentation


class Counter(object):
    def __init__(self, start=0):
        self.v = start

    def increase(self):
        self.v += 1

    def decrease(self):
        self.v -= 1


@presentation.render_for(Counter)
def render(self, h, comp, *args):
    h.head.css_url('counter.css')

    with h.div(class_='counter'):
        h << h.div(self.v)

        with h.span:
            h << h.a(u'\N{MINUS SIGN}', title='decrease').action(self.decrease)

        with h.span:
            h << h.a('=', title='freeze').action(comp.becomes, model='freezed')

        with h.span:
            h << h.a(u'\N{PLUS SIGN}', title='increase').action(self.increase)

    return h.root


@presentation.render_for(Counter, model='freezed')
def render(self, h, *args):
    h.head.css_url('counter.css')

    with h.div(class_='counter'):
        h << h.div(self.v)

        with h.span:
            h << h.a(u'\N{MINUS SIGN}', class_='disabled')

        with h.span:
            h << h.a('=', class_='disabled')

        with h.span:
            h << h.a(u'\N{PLUS SIGN}', class_='disabled')

    return h.root


# -----------------------------------------------------------------------------

hl_lines = (
    range(13, 60),
    (
        (13,),
        '<p>Default view for a <code>Counter</code> component</p>'
        '<p>Parameters are:'
        '<ol>'
        '<li><code>self</code>: the <code>Counter</code> object</li>'
        '<li><code>h</code>: a HTML renderer</li>'
        '<li><code>comp</code>: the component wrapping the '
        '<code>Counter</code> object</li></ol>',
        range(13, 29)
    ),

    (
        (20,),
        'Direct association of the <code>decrease</code> method to a link',
        (20,)
    ),

    (
        (26,),
        'Direct association of the <code>increase</code> method to a link',
        (26,)
    ),

    (
        (23,),
        '<p>After a click on the link, the component will be rendered with its '
        '<code>freezed</code> view: the <code>becomes()</code> method of the '
        'component is used to change it by the same object but with a different '
        'view</p>',
        (23,)
    ),

    (
        (31,),
        '<p>Named view <code>freezed</code> for a <code>Counter</code> component',
        range(31, 48)
    ),
)
