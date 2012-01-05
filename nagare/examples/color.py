#--
# Copyright (c) 2008-2012 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
#--

"""Examples to demonstrate the embedding, binding, replacing and
call/answer of components"""
 
from nagare import component
from nagare import presentation

class ColorChooser:
    """A simple object"""
    pass

@presentation.render_for(ColorChooser)
def render(self, h, comp, *args):
    """This view answered the color clicked
    
    In:
      - ``h`` -- the renderer
      - ``comp`` -- the component
      
    Return:
      - the view
    """
    return (
            h.a('X', style='background-color: #4B96FF').action(lambda: comp.answer('#4B96FF')),
            h.a('X', style='background-color: #FF8FDF').action(lambda: comp.answer('#FF8FDF')),
            h.a('X', style='background-color: #9EFF5D').action(lambda: comp.answer('#9EFF5D')),
            h.a('X', style='background-color: #FFFFFF').action(lambda: comp.answer('#FFFFFF'))
           )
    # Could also be written as:
    #return [h.a('X', style='background-color:' + color).action(lambda c=color: comp.answer(c))
    #        for color in ('#4B96FF', '#FF8FDF', '#9EFF5D', '#FFFFFF')]

"""
@presentation.render_for(ColorChooser, model='meta')
def render(self, h, *args):
    return h.h1(self.id)
"""

class Text:
    """A colorised text"""
    def __init__(self, text='', color='#ffffff'):
        """Initialization
        
        In:
          - ``text``
          - ``color`` -- background color of the text
        """
        self.color = color
        self.text = text

    def set_color(self, color):
        """Change the background color
        
        In:
          - ``color`` -- new background color of the text
        """
        self.color = color

@presentation.render_for(Text)
def render(self, h, *args):
    """This view renders the text on a colorised background
    
    In:
      - ``h`` -- the renderer
      
    Return:
      - the view
    """
    return h.span(self.text, style='background-color: '+self.color)

"""
@presentation.render_for(Text, model='meta')
def render(self, h, *args):
    return h.h2('Text')
"""

# ---------------------------------------------------------------------------

# This example:
#
# - render a component

def example1():
    return Text('Hello world !', 'lightgreen')
    
examples = ('A simple colorised text', example1)

# -------------------------------------------------------------------------------------------------------

# This example:
#
# - embed and bind components

class App1:
    """This component:
    
      - embeds 2 components: a text component and a color chooser
      - bind the answer of the color chooser (the selected color) to the
        ``set_color()`` method of the text component
    """
    def __init__(self):
        self.text = component.Component(Text('Hello world !'))

        self.chooser = component.Component(ColorChooser())
        self.chooser.on_answer(self.text().set_color)   # Binding

@presentation.render_for(App1)
def render(self, h, *args):
    """This view renders the 2 embedded components
    
    In:
      - ``h`` -- the renderer
      
    Return:
      - the view
    """    
    return (self.chooser, h.br, self.text)

@presentation.render_for(App1, model='meta')
def render(self, h, *args):
    return h.h2('Yeah !')

examples += ('Embedding and binding components', App1)

# -------------------------------------------------------------------------------------------------------

# This example:
#
# - embed and bind components

class App2:
    """This component implement a simple workflow:
    
      1. display the text component
      2. replace the text component to display the color chooser
      3. after a color is selected, display the text component with this
         color
    """    
    def __init__(self):
        self.text = component.Component(Text('Hello world !'))

    def change_text_color(self, comp):
        """Replace the text component with the color chooser by calling it.
        Then, as the color chooser answers with the selected color, set the color
        text with it
        
        In:
          - ``comp`` -- the component to replace by the color chooser
        """
        # Temporary replace the component by the color chooser
        color = comp.call(ColorChooser())
        
        # Set the background color of the text with the selected color
        self.text().set_color(color)

@presentation.render_for(App2)
def render(self, h, comp, *args):
    """This view renders the 2 embedded components
    
    In:
      - ``h`` -- the renderer
      - ``comp`` -- the component
      
    Return:
      - the view
    """    
    return (
             h.a('Change the color').action(lambda: self.change_text_color(comp)),
             h.br,
             self.text,
            )

examples += ("Call / answer of a component", App2)

# -------------------------------------------------------------------------------------------------------

# This example:
#
# - illustrate that the same object can be displayed several time with
#   different views

class App3:
    def __init__(self):
        self.app = component.Component(App1())

@presentation.render_for(App3)
def render(self, h, *args):
    """This view renders twice the same component but with different views
    (the default view and the ``meta`` view)
    
    In:
      - ``h`` -- the renderer
      
    Return:
      - the view
    """        
    return h.table(h.tr(
                        # The component is rendered with the default view
                        h.td(self.app, align='center'),
                        
                        # The component is rendered with the ``meta`` view
                        h.td(self.app.render(h, model='meta'), align='center')
                       ))

examples += ('Twice the same component with 2 different views', App3)

# -------------------------------------------------------------------------------------------------------

# This example:
#
# - demonstrate that each component follow its own workflow

class Double:
    def __init__(self):
        self.left  = component.Component(App1())
        self.right = component.Component(App2())

@presentation.render_for(Double)
def render(self, h, *args):
    return h.table(h.tr(h.td(self.left, align='center'),
                        h.td(self.right, align='center')))

examples += ('2 independante components', Double)
