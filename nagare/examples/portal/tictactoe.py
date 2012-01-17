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
from nagare import component, presentation, util

class TicTacToe:
    def __init__(self):
        self._board = [0]*9

    def played(self, player, played):
        self._board[played] = player

    def is_won(self):
        for (c1, c2, c3) in ((0, 1, 2), (3, 4, 5), (6, 7, 8),
                             (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6)):
            if self._board[c1] and (self._board[c1] == self._board[c2] == self._board[c3]):
                return True

        return False

    def is_ended(self):
        return all(self._board)

@presentation.render_for(TicTacToe)
def render(self, h, comp, *args):
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

class Task(component.Task):
    def go(self, comp):
        while True:
            board = TicTacToe()

            players = (comp.call(util.Ask('Player #1')),
                       comp.call(util.Ask('Player #2')))

            player = 1
            while not board.is_won() and not board.is_ended():
                player = (player+1) & 1

                played = comp.call(component.Component(board))
                board.played(player+1, played)

            if board.is_won():
                msg =  'Player %s WON !' %  players[player]
            else:
                msg = 'Nobody WON !'

            comp.call(util.Confirm(msg))

# -----------------------------------------------------------------------------

hl_lines = (
    range(12, 72),
    (
        (4,),
        'Definition of a Plain Old Python Object',
        range(4, 21)
    ),

    (
        (22,),
        '<p>Definition of its default HTML view</p>'
        '<p>Parameters are:'
        '<ol>'
        '<li><code>self</code>: the <code>TicTacToe</code> object</li>'
        '<li><code>h</code>: a HTML renderer</li>'
        '<li><code>comp</code>: the component wrapping the <code>TicTacToe</code> object</li>'
        '</ol>',
        range(22, 39)
    ),

    (
        (33, 52),
        '<p>Use of the <code>call()/answer()</code> mechanism: the task calls a <code>TictacToe</code> component</p>'
        '<p>When an empty cell is clicked, the cell index is sent back to the task '
        'as <code>played</code></p>',
        (33, 52)
    ),

    (
        (40,),
        'A <code>component.Task</code> uses continuations to implement the '
        'TicTacToe logic in pure linear Python code',
        range(40, 61)
    ),

    (
        (45, 60),
        'Usage of the Nagare components <code>util.Ask</code> '
        'and <code>util.Confirm</code>',
        (45, 46, 60)

    )
)
