#--
# Copyright (c) 2008, 2009, 2010 Net-ng.
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

        return ''

@presentation.render_for(Calculator)
def render(self, h, *args):
    """Rendering of the RPN calculator
    
    In:
      - ``h`` -- the renderer
      
    Return:
      - the view
    """    
    return (
            'Value: ', self.get_last(), h.br,

            h.a(1).action(lambda: self.digit(1)), ' ',
            h.a(2).action(lambda: self.digit(2)), ' ',
            h.a(3).action(lambda: self.digit(3)), ' ',
            h.br,
            h.a(4).action(lambda: self.digit(4)), ' ',
            h.a(5).action(lambda: self.digit(5)), ' ',
            h.a(6).action(lambda: self.digit(6)), ' ',
            h.br,
            h.a(7).action(lambda: self.digit(7)), ' ',
            h.a(8).action(lambda: self.digit(8)), ' ',
            h.a(9).action(lambda: self.digit(9)), ' ',
            h.br,
            h.a(0).action(lambda: self.digit(0)),
            h.br,
            h.a('Enter').action(self.enter),
            h.br,
            h.a('+').action(lambda: self.operand(operator.__add__)), ' ',
            h.a('-').action(lambda: self.operand(operator.__sub__)), ' ',
            h.a('/').action(lambda: self.operand(operator.__div__)), ' ',
            h.a('*').action(lambda: self.operand(operator.__mul__)),
            h.br,
            h.a('Drop').action(self.drop),
           )

examples = ('RPN calculator', Calculator)
