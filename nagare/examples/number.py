#--
# Copyright (c) 2008-2012 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
#--

import random

from nagare import component, util, state

# ---------------------------------------------------------------------------

class Number(component.Task):
    """A little game to guess a number
    """
    def __init__(self, final_text):
        self.final_text = final_text
        
    def go(self, comp):
        """The game algorithm, using continuation for a pure linear Python code
        
        In:
          - ``comp`` -- this component
        """
        self.attempt = 1
        number = random.randint(1, 20)
        
        comp.call(util.Confirm('I choose a number between 1 and 20. Try to guess it'))
        
        while True:
            x = comp.call(util.Ask('Try #%d: ' % self.attempt))
            if not x.isdigit():
                continue
            
            x = int(x)
            
            if x > number:
                comp.call(util.Confirm('Choose a lower number'))
                
            if x < number:
                comp.call(util.Confirm('Choose a greater number'))
                
            if x == number:
                comp.call(util.Confirm(self.final_text % self.attempt))
                break

            self.attempt += 1

# ---------------------------------------------------------------------------

# This example shows that, by default, the objects are statefull

def example1():
    # By default, an object is statefull
    number = Number('''You found the secret number in %d tries.
Now use the 'back' button to cheat : go back to the first attempt and enter the correct number''')
    return number

examples = ('A statefull component', example1)

# ---------------------------------------------------------------------------

# This example shows how to create stateless objects

def example2():
    number = Number('''You found the secret number in %d tries.
Now use the 'back' button to cheat : you CAN'T''')
    
    # The object is made stateless
    number = state.stateless(number)
    
    return number

examples += ('A stateless component', example2)
