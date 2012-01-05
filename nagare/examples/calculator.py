#--
# Copyright (c) 2008-2012 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
#--

"""A RPN calculator"""

import operator
from nagare import presentation

class Calculator:
    """A RPN calculator object with methods to manage the stack
    """
    def __init__(self):
        """Initialisation"""
        self.display = ''   # Number displayed
        self.stack = []     # RPN stack

    def digit(self, digit):
        """A new digit is entered

        In:
          - ``digit``
        """
        self.display += str(digit)

    def enter(self):
        """The ``enter`` is pressed, push the number displayed onto the stack
        """
        if self.display:
            self.stack.append(int(self.display))
            self.display = ''

    def operand(self, op):
        """Do a calculus. Push the result onto the stack.

        In:
          - ``op`` -- 2 operands function
        """
        self.enter()

        if len(self.stack) >= 2:
            v = self.stack.pop()
            self.stack[-1] = op(self.stack[-1], v)

    def drop(self):
        """Clear the display or drop the top of the stack"""
        if self.display:
            self.display = ''
            return

        if not self.stack:
            return

        self.stack.pop()

    def get_last(self):
        """Return the number displayed or the top of the stack

        Return:
          - the number
        """
        if self.display:
            return self.display

        if self.stack:
            return str(self.stack[-1])

        return '0'

@presentation.render_for(Calculator)
def render(self, h, *args):
    """Rendering of the RPN calculator

    In:
      - ``h`` -- the renderer

    Return:
      - the view
    """
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

examples = ('RPN calculator', Calculator)

