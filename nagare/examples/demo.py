#--
# Copyright (c) 2008, Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
#--

from __future__ import with_statement

from nagare import component, presentation

# Modules where the examples are located
import counter
import calculator
import color
import tictactoe
import form
import number

# ---------------------------------------------------------------------------

class TreeView(object):
    """This component display a 2-levels tree
    """
    def __init__(self, nodes, label):
        """Initialization
        
        In:
          - ``nodes`` -- list of list
          - ``label`` -- prefix label to display for the 2nd level nodes
        """
        self.nodes = nodes
        self.label = label
        
        self._selected = 0   # The currently selected nodes
        
    def selected(self, comp, i, n, name, data):
        """A new 2nd level node is selected
        
        In:
          - ``comp`` -- this component
          - ``i`` -- index of the selected node
          - ``n`` -- the new selected node
          - ``name`` -- label of the first level node (the parent)
          - ``data`` -- data of the selected 2nd level node
        """
        self._selected = n
        comp.answer((name, i, data))
        
    def select(self, comp, category, n):
        node = 0
        for (name, level2_nodes) in self.nodes:
            if name == category:
                if n < len(level2_nodes):
                    node += n
                    self.selected(comp, n, node, name, level2_nodes[n])
                    return True
            else:
                node += len(level2_nodes)

        return False
        
        
@presentation.render_for(TreeView)
def render(self, h, comp, *args):
    node = 0

    # Display a list of lists
    with h.ul(style='padding-right: 10px; border-right: solid 3px #eee'):
        for (name, level2_nodes) in self.nodes:
            # First level, display the name of the node
            with h.li(name.capitalize()):
                with h.ul:
                    for (i, data) in enumerate(level2_nodes):
                        # Second level, display a selectable label
                        with h.li as li:
                            if node == self._selected:
                                # Currently selected node
                                li.set('style', 'background-color: #eee')
                                h << self.label + str(i+1)
                            else:
                                # Selectable node
                                h << h.a(self.label + str(i+1), href='%s/%d' % (name, i+1)).action(lambda i=i, node=node, name=name, data=data: self.selected(comp, i, node, name, data))

                            node += 1

    return h.root

# ---------------------------------------------------------------------------

class Examples(object):
    """Display the UI to browse the examples
    """
    def __init__(self, title, label, repository_path, examples):
        """Initialization
        
        In:
          - ``title`` -- title to display
          - ``label`` -- prefix label to display for the 2nd level nodes 
          - ``repository_path`` -- url template to display the module code
          - ``examples`` -- tree of examples
        """
        self.title = title
        self.repository_path = repository_path
        
        # The ``example`` component, displayed on the right side of the
        # screen. It will be replaced each time an example is selected
        self.example = component.Component(None)

        # Display the first example found
        self.change_example((examples[0][0], 0, examples[0][1][0]))
        
        # The ``tree_view`` component, displayed on the left side of the
        # screen. It will answered the selected example
        self.tree_view = component.Component(TreeView(examples, label))
        
        # Each time an example is selected into the tree view, call the
        # ``change_example()`` method
        self.tree_view.on_answer(self.change_example)

    def change_example(self, (module_name, i, (description, comp))):
        """A new example is selected
        
        In:
          - ``module_name`` -- name of the module where the example is located
          - ``description`` -- description of the example
          - ``comp`` -- root component of the example
        """
        self.module_name = module_name
        self.description = description

        # Change the right side of the screen with the example
        self.example.becomes(comp(), url='%s/%d' % (module_name, i+1))
        
@presentation.render_for(Examples)
def render(self, h, comp, *args):
    """Display the full UI
    """
    # Add some CSS into the page header
    h.head.css_url('/static/nagare/application.css')    
    h.head.css('examples', '''
    #description {
        border: dashed 1px;
        padding: 5px;
        background-color: #eee;
        font-style: italic;
        width: 95%;
    }
    
    #example {
        padding-left: 10px;
        padding-top: 25px;
        vertical-align: top;
        width: 100%;
    }
    
    #source {
        text-align: right;
        font-size: 0.7em;
        padding-right: 30px;
    }
    ''')
    h.head << h.head.title('Nagare examples')

    with h.div(class_='mybody'):
        # Create the page banner
        with h.div(id='myheader'):
            h << h.a(h.img(src='/static/nagare/img/logo.gif'), id='logo', href='http://www.nagare.org/', title='Nagare home')
            h << h.span(self.title, id='title')
    
        with h.div(id='main'):
            # Create a table with, into the left column, the tree view of the examples
            # and, into the right column the currently selected example
            with h.table(width='100%'):
                with h.tr:
                    # Display the tree view
                    h << h.td(self.tree_view, valign='top')
                    
                    # Display the currently selected example
                    with h.td(id='example'):
                        h << h.div(self.description, id='description')
                        with h.div(id='source'):
                            h << h.a('View the source', href=self.repository_path % self.module_name)
                            h << h.br
                        h << self.example

    h << h.div(class_='footer')

    return h.root

@presentation.init_for(Examples, "len(url) >= 2")
def init(self, url, request, *args):
    (name, n) = url[:2]
    r = self.tree_view().select(self.tree_view, name, int(n)-1)
    if not r:
        return presentation.NOT_FOUND
    
    if len(url) > 2:
        return self.example.init(url[2:], request)
    
    return presentation.FOUND
    
# ---------------------------------------------------------------------

def module_name(name):
    """From a full Python module name, return only the module name
    
    In:
      - ``name`` -- Python module name
      
    Return:
      - module name
    """
    # Keep only the last part of the path
    return name.rsplit('.', 1)[1]


# Modules where to located the ``examples`` list
modules = (counter, calculator, color, tictactoe, number, form)

# Create a tree with, at the first level, the module name and, at the second
# level, a list of tuples (example description, example factory)
examples = [(module_name(module.__name__), zip(module.examples[::2], module.examples[1::2])) for module in modules]

# TRAC url to display a module code from the SVN repository
SVN_EXAMPLES_URL = 'http://www.nagare.org/trac/browser/trunk/nagare/examples/nagare/examples/%s.py'

app = lambda: Examples('Demo', 'Demo', SVN_EXAMPLES_URL, examples)
