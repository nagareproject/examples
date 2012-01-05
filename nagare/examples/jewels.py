#--
# Copyright (c) 2008-2012 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
#--

from __future__ import with_statement

import random

from nagare import component, presentation, util

class Board(object):
    """The Jewels board
    """
    NB_IMGS = 3

    def __init__(self, cols, rows):
        """Initialization

        In:
          - ``cols`` -- board width
          - ``rows`` -- board height
        """
        # Create an (cols+2)*(rows+2) array
        # (one empty row and col around the board)
        self.matrix = [[None]*(rows+2) for j in xrange(cols+2)]

        # Initialization each cells with a random jewel
        for i in xrange(1, rows+1):
            for j in xrange(1, cols+1):
                self.matrix[j][i] = random.randint(1, self.NB_IMGS)

        self.score = 0

    def is_finish(self):
        """Test if the game is finished

        Return:
          - a boolean
        """
        r = False

        # Test if two adjacent cells in a row have the same jewel
        for row in self.matrix:
            r |= any(a==b for (a, b) in zip(row, row[1:]) if a)

        # Test if two adjacent cells in a column have the same jewel
        for col in zip(*self.matrix):
            r |= any(a==b for (a, b) in zip(col, col[1:]) if a)

        return not r

    def flood(self, i, j, jewel):
        """Empty all the connected cells with the same jewel

        In:
          - ``i``, ``j`` -- the current cell to test
          - ``jewel`` -- the jewel to test

        Return:
          - number of connected cells
        """
        if self.matrix[j][i] != jewel:
            # The current cell has not this jewel
            # Stop the recursion
            return 0

        # Empty the current cell
        self.matrix[j][i] = None

        # Check all the adjacent cells
        return 1 + self.flood(i-1, j, jewel) + self.flood(i+1, j, jewel) + self.flood(i, j-1, jewel) + self.flood(i, j+1, jewel)

    def collapse(self):
        """Collapse the empty cells
        """
        self.matrix = [sorted(l, key=bool)[1:]+[None] for l in self.matrix]

        self.matrix.sort(key=any, reverse=True)
        self.matrix.insert(0, self.matrix.pop())

    def played(self, i, j):
        """Play a selected cell

        In:
          - ``i``, ``j`` -- the selected cell
        """
        jewel = self.matrix[j][i]
        n = self.flood(i, j, jewel) # Empty the connected cells

        # Add to the score: ((nb of removed cells) - 2) ** 2
        if n == 1:
            self.matrix[j][i] = jewel
        else:
            self.score += (n-2)**2

        self.collapse()

@presentation.render_for(Board)
def render(self, h, comp, *args):
    with h.div(class_='jewels'):
        h << h.h1('Score: ', self.score)

        with h.table:
            for (i, row) in enumerate(zip(*self.matrix)[1:-1]):
                with h.tr:
                    for (j, jewel) in enumerate(row[1:-1]):
                        with h.td(class_='cell%d' % ((i+j) % 2)):
                            if jewel:
                                # Clicking on a cell with a jewel answers the tuple (i, j)
                                with h.a.action(lambda i=i+1, j=j+1: comp.answer((i, j))):
                                    h << h.img(src='jewel%d.gif' % jewel)

    return h.root

# -----------------------------------------------------------------------------

class Jewels(component.Task):
    """The Jewels game
    """
    def __init__(self, cols, rows):
        """Initialization

        In:
          - ``cols`` -- board width
          - ``rows`` -- board height
        """
        self.cols = cols
        self.rows = rows

    def go(self, comp):
        # Create the board
        board = Board(self.cols, self.rows)

        while not board.is_finish():
            # Wait for a click in a cell
            played = comp.call(component.Component(board))

            # Play it
            board.played(*played)

        comp.call(util.Confirm('No movements left, you scored %s.' % board.score))

# -----------------------------------------------------------------------------

class App(object):
    """Jewels game example
    """

    def __init__(self):
        """Initialization
        """
        # Create a jewels component with a default size
        self.jewels = component.Component(Jewels(15, 10))

@presentation.render_for(App)
def render(self, h, *args):
    h.head.css('jewels', '''
        body {
            background-color: #335577;
            font-family: Verdana;
        }''')

    h.head.css_url('jewels.css')
    h.head << h.head.title('Jewels')

    with h.div(class_='jewels'):
        h << self.jewels

    return h.root

# -----------------------------------------------------------------------------

app = App
