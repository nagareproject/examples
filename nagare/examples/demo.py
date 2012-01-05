#--
# Copyright (c) 2008-2012 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
#--

from __future__ import with_statement

from nagare import component, presentation, var

# Modules where the examples are located
import counter
import calculator
import color
import tictactoe
import form
import number

# ---------------------------------------------------------------------------

class Menu(object):
    """This component displays a menu
    """
    def __init__(self, labels, selected=0):
        """Initialization

        In:
          - ``labels`` -- list of menu entries (title, url)
          - ``selected`` -- selected label
        """
        self.labels = labels
        self._selected = selected   # The currently selected label

@presentation.render_for(Menu)
def render(self, h, comp, *args):
    with h.ul(class_='menu'):
        for (i, (label, href)) in enumerate(self.labels):
            # When clicked, an entry answers with its index
            a = h.a(label, href=href).action(lambda i=i: comp.answer(i))
            if i == self._selected:
                a(class_='selected')

            h << h.li(a)

    return h.root

# ---------------------------------------------------------------------------

class Examples(object):
    """Display the UI to browse the examples
    """
    def __init__(self, title, repository_path, examples):
        """Initialization

        In:
          - ``title`` -- title to display
          - ``repository_path`` -- url template to display a module code
          - ``examples`` -- list of examples
        """
        self.title = title
        self.repository_path = repository_path
        self.examples = examples

        # The ``example`` component is displayed on the right side of the
        # screen. It will be replaced each time an example is selected
        self.example = component.Component(None)

        # The ``tree_view`` component is displayed on the left side of the
        # screen. It will answered the selected example
        self.level1_menu = component.Component(None)

        # Each time an example is selected in the menu, call the
        # ``change_example()`` method
        self.level1_menu.on_answer(self.change_example)

        self.level2_menu = component.Component(None)
        self.level2_menu.on_answer(self.change_step)

        # Select the first example
        self.change_example(0)

    def change_example(self, i):
        """A new example is selected

        In:
          - ``i`` -- index of the example to select
        """
        self.selected_examples = i;
        self.module_name = self.examples[i][0]

        self.level1_menu.becomes(Menu([(label.capitalize(), label) for (label, _) in self.examples], i))

        self.change_step(0)

    def change_step(self, i):
        """A new step of the current example is selected

        In:
          - ``i`` -- step to select
        """
        selected_examples = self.examples[self.selected_examples][1]
        self.description = selected_examples[i][0]

        self.example.becomes(selected_examples[i][1](), url='%s/%d' % (self.module_name, i+1))

        if len(selected_examples) != 1:
            labels = [('%s %d' % (self.module_name, j), j) for j in range(1, len(selected_examples)+1)]
            self.level2_menu.becomes(Menu(labels, i), url=self.module_name)
        else:
            self.level2_menu.becomes(None)

@presentation.render_for(Examples)
def render(self, h, comp, *args):
    """Display the full UI
    """
    # Add some CSS into the page header
    h.head.css_url('/static/nagare/application.css')
    h.head.css_url('demo.css')

    h.head << h.head.title(self.title)

    with h.div(id='body'):
        h << h.a(h.img(src='/static/nagare/img/logo.png'), id='logo', href='http://www.nagare.org/', title='Nagare home')

        with h.div(id='content'):
            h << h.div(self.title, id='title')

            h << h.div(self.level1_menu, id='mainnav', class_='horizontal')

            with h.div(id='main'):
                if self.level2_menu():
                    h << h.div(self.level2_menu, id='steps')

                with h.div(id='example', class_='example_right' if self.level2_menu() else 'example_full' ):
                    h << h.div(self.description, class_='note')

                    with h.div(id='source'):
                        h << h.a('View the source', href=self.repository_path % self.module_name)

                    h << self.example

    return h.root

# ---------------------------------------------------------------------

@presentation.init_for(Examples, "len(url) == 1")
def init(self, url, comp, http_method, request):
    example_name = url[0]

    try:
        example = [x[0] for x in self.examples].index(example_name)
    except ValueError:
        raise presentation.HTTPNotFound()

    self.change_example(example)

@presentation.init_for(Examples, "len(url) >= 2 and http_method == 'GET'")
def init(self, url, comp, http_method, request):
    comp.init(url[:1], http_method, request)

    step = url[1]

    try:
        step = int(step)
    except ValueError:
        raise presentation.HTTPNotFound()

    if (step <= 0) or (step > len(self.examples[self.selected_examples][1])):
        raise presentation.HTTPNotFound()

    self.change_step(step-1)

    if len(url) > 2:
        self.example.init(url[2:], http_method, request)

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

# Create the examples list
examples = [(module_name(module.__name__), zip(module.examples[::2], module.examples[1::2])) for module in modules]

# TRAC url to display a module code from the Mercurial repository
HG_EXAMPLES_URL = 'http://www.nagare.org/trac/browser/examples/nagare/examples/%s.py'

app = lambda: Examples('Demo', HG_EXAMPLES_URL, examples)
