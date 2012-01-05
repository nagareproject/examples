#--
# Copyright (c) 2008-2012 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
#--

"""Examples to demonstrate the separation between UI components
and a logic component implemented as a ``component.Task``
"""

from __future__ import with_statement

import operator

from nagare import component, presentation, util

# ---------------------------------------------------------------------------

class TicTacToe:
    """The TicTacToe board
    """
    def __init__(self):
        """Initialization
        """
        # TicTacToe board as a linear list of cell
        self._board = [0]*9

    def played(self, player, played):
        """A cell was played
        
        In:
          - ``player`` -- id of the player that has played (1 or 2)
          - ``played`` -- the cell
        """
        self._board[played] = player

    def is_won(self):
        """Review all the cells played to check is the game is won
        
        Return:
          - a boolean: is the game ended and won ?
        """
        # Game won if 3 consecutive cells were played by the same player
        for (c1, c2, c3) in ((0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6)):
            if self._board[c1] and (self._board[c1] == self._board[c2]) and (self._board[c2] == self._board[c3]):
                return True

        return False

    def is_ended(self):
        """Review all the cells playes to see if the game is ended (no more
        free cells)
        
        Return:
          - a boolean: is the game ended ?
        """
        return all(self._board)

@presentation.render_for(TicTacToe)
def render(self, h, comp, *args):
    """Render the board in a table of 3*3 cells. The free cells are clickable
    and answer their indice
    
    In:
      - ``h`` -- the renderer
      - ``comp`` -- the component
      
    Return:
      - the view
    """
    h.head.css_url('tictactoe.css')

    with h.table(class_='tictactoe'):
        i = 0
        for row in zip(self._board[::3], self._board[1::3], self._board[2::3]):
            with h.tr:
                for x in row:
                    with h.td:
                        if x == 0:
                            h << h.a('-').action(lambda i=i: comp.answer(i))
                        else:
                            h << ('X' if x==1 else 'O')

                        i += 1
    return h.root

# ---------------------------------------------------------------------------

class Task(component.Task):
    """This ``component.Task`` uses continuations to implement the TicTacToe
    logic in pure linear Python code
    """
    
    def go(self, comp):
        while True:
            # 1. Create the board
            board = TicTacToe()

            # 2. Ask the names of the players
            players = (comp.call(util.Ask('Player #1')), comp.call(util.Ask('Player #2')))
    
            player = 1
            # 3. Play the game until a player wins or there are no more free cells
            while not board.is_won() and not board.is_ended():
                player = (player+1) & 1 # Toggle the player
    
                # Display the board and get the clicked cell
                played = comp.call(component.Component(board))
                
                # Register the clicked cell
                board.played(player+1, played)
    
            if board.is_won():
                msg =  'Player %s WON !' %  players[player]
            else:
                msg = 'Nobody WON !'
    
            # 4. Display the end message
            comp.call(util.Confirm(msg))

examples = ("Using a component.Task() to implement the game logic", Task)


# ---------------------------------------------------------------------------

# This example:
#
# - shows how to render a component with an asynchronous renderer
# - shows that the code of a component doesn't need to be modified to
#   become asynchronous

class App(object):
    def __init__(self):
        self.inner = component.Component(Task())

@presentation.render_for(App)
def render(self, h, *args):
    return self.inner.render(h.AsyncRenderer())

examples += ('Automatic use of asynchronous requests/updates', App)

# ---------------------------------------------------------------------------

class Double:
    def __init__(self):
        # Incremented each time the page is fully re-generated
        self.nb_display = 0

        # 2 different components of the same type
        self.left = component.Component(Task())
        self.right = component.Component(Task())

@presentation.render_for(Double)
def render(self, h, binding, *args):
    self.nb_display += 1

    with h.div:
        h << h.div('Full page generations: ',  self.nb_display)

        with h.div(style='float: left'):
            h << h.div('Synchronous', style='text-align: center; margin-top: 10px')

            # The ``left`` component is rendered with a standard HTML renderer
            h << self.left

        with h.div(style='float: right'):
            h << h.div('Asynchronous', style='text-align: center; margin-top: 10px')

            # The ``right`` component is rendered with an asynchronous HTML renderer
            h << h.td(self.right.render(h.AsyncRenderer()))

    return h.root

examples += ('Mixing 2 synchronous / asynchronous components', Double)
