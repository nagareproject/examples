#--
# Copyright (c) 2008-2012 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
#--

from __future__ import with_statement

import operator
from nagare import presentation

class Calculator:
    def __init__(self):
        self.display = ''
        self.stack = []

    def digit(self, digit):
        self.display += str(digit)

    def enter(self):
        if self.display:
            self.stack.append(int(self.display))
            self.display = ''

    def operand(self, op):
        self.enter()

        if len(self.stack) >= 2:
            v = self.stack.pop()
            self.stack[-1] = op(self.stack[-1], v)

    def drop(self):
        if self.display:
            self.display = ''
            return

        if not self.stack:
            return

        self.stack.pop()

    def get_last(self):
        if self.display:
            return self.display

        if self.stack:
            return str(self.stack[-1])

        return '0'

@presentation.render_for(Calculator)
def render(self, h, *args):
    h.head << h.head.css_url('calculator.css')

    with h.div(class_='calculator'):
        h << h.div(self.get_last(), class_='calculator_display')

        with h.table:
            with h.tr:
                h << h.td(colspan=3)
                h << h.td(h.a('C').action(self.drop))
                h << h.td(h.a(u'\N{DIVISION SIGN}').action(lambda: self.operand(operator.div)))

            with h.tr:
                h << h.td(h.a(7).action(lambda: self.digit(7)))
                h << h.td(h.a(8).action(lambda: self.digit(8)))
                h << h.td(h.a(9).action(lambda: self.digit(9)))
                h << h.td
                h << h.td(h.a(u'\N{MULTIPLICATION X}').action(lambda: self.operand(operator.mul)))

            with h.tr:
                h << h.td(h.a(4).action(lambda: self.digit(4)))
                h << h.td(h.a(5).action(lambda: self.digit(5)))
                h << h.td(h.a(6).action(lambda: self.digit(6)))
                h << h.td
                h << h.td(h.a(u'\N{MINUS SIGN}').action(lambda: self.operand(operator.sub)))

            with h.tr:
                h << h.td(h.a(1).action(lambda: self.digit(1)))
                h << h.td(h.a(2).action(lambda: self.digit(2)))
                h << h.td(h.a(3).action(lambda: self.digit(3)))
                h << h.td
                h << h.td(h.a(u'\N{PLUS SIGN}').action(lambda: self.operand(operator.add)))

            with h.tr:
                h << h.td
                h << h.td(h.a(0).action(lambda: self.digit(0)))
                h << h.td(colspan=2)
                h << h.td(h.a(u'\N{WHITE RIGHT-POINTING POINTER}').action(self.enter))

    return h.root

# -----------------------------------------------------------------------------

hl_lines = (
    range(12, 95),
    (
        (4,),
        'Definition of a Plain Old Calculator Python Object',
        range(4, 42)
    ),

    (
        (43,),
        '<p>Default view for a <code>Calculator</code></p>'
        '<p>Parameters are:'
        '<ol>'
        '<li><code>self</code>: the <code>Calculator</code> object</li>'
        '<li><code>h</code>: a HTML renderer</li>'
        '</ol>',
        range(43, 84)
    ),

    (
        (53,),
        'Direct association of the <code>drop</code> method to a link',
        (53,)
    ),

    (
        (54, 61, 68, 75),
        'Use of anonymous functions to call the <code>operand</code> method',
        (54, 61, 68, 75)
    ),

    (
        (57, 58, 59, 64, 65, 66, 71, 72, 73, 79),
        'Use of anonymous functions to call the <code>digit</code> method',
        (57, 58, 59, 64, 65, 66, 71, 72, 73, 79)
    ),

    (
        (81,),
        'Direct association of the <code>enter</code> method to link',
        (81,)
    )
)
