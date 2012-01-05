#--
# Copyright (c) 2008-2012 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
#--

from __future__ import with_statement

from nagare import presentation, component, comet, var, ajax

# -----------------------------------------------------------------------------

@ajax.javascript
def append_msg(msg):
    # Add a ``<li>`` to the ``<ul>`` list with id ``msgs``
    #
    # This function is translated to javascript and executed on the browser
    #
    # In:
    #   - ``msg`` -- message to add

    # Create the ``<li>`` element, filled with the message text
    li = document.createElement('li')
    li.appendChild(document.createTextNode(msg))
    li.setAttribute('class', 'msg_type_'+msg.substring(0, 1))

    msgs = document.getElementById('msgs')

    # The ``<li>`` becomes the first child of the list
    if not msgs.childNodes.length:
        msgs.appendChild(li)
    else:
        msgs.insertBefore(li, msgs.firstChild)

# -----------------------------------------------------------------------------

class User(object):
    """User interactions
    """
    def __init__(self):
        """Initialization
        """
        self.user = var.Var()   # The user name

    def logout(self, comp):
        """The user wants to quit the chat room

        In:
          - ``comp`` -- this component
        """
        comp.answer(('part', self.user()))
        self.user(None)

@presentation.render_for(User)
def render(self, h, comp, *args):
    msg = var.Var()

    if not self.user():
        # If the user is not connected, generate the login form
        # -----------------------------------------------------

        with h.form:
            h << "What's your name: " << h.input.action(self.user)
            h << h.input(type='submit', value='Enter the room').action(lambda: comp.answer(('join', self.user())) )
    else:
        # If the user is connected, generate the form to enter and send a message
        # -----------------------------------------------------------------------

        with h.div:
            h << h.a('Logout').action(lambda: self.logout(comp))

            with h.form:
                h << h.input(size=50).action(msg) << ' '
                h << h.input(type='submit', value='Send').action(lambda: comp.answer(('send', self.user(), msg())))

    return h.root

# -----------------------------------------------------------------------------

class Chat(object):
    """Chat room logic
    """
    def __init__(self, channel_id):
        """Initialization

        In:
          - ``channel_id`` -- identifier of the push channel to use
        """
        self.channel_id = channel_id

        self.interaction = component.Component(User())
        self.interaction.on_answer(self.actions)    # Dispatch on the answer

        # Create the push channel
        # ``append_msg.name`` is the name of the generated javascript function
        comet.channels.create(channel_id, append_msg.name)

    def actions(self, args):
        """Actions dispatcher

        In:
          - ``args`` -- ``args[0]`` is the action name, ``args[1:]`` its parameters
        """
        getattr(Chat, args[0])(self, *args[1:])

    def join(self, user):
        """A user enters the chat room

        In:
          - ``user`` -- the user name
        """
        comet.channels.send(self.channel_id, 'join: '+user)

    def part(self, user):
        """A user quits the chat room

        In:
          - ``user`` -- the user name
        """
        comet.channels.send(self.channel_id, 'part: '+user)

    def send(self, user, msg):
        """A user sends a message to the chat room

        In:
          - ``user`` -- the user name
          - ``msg`` -- the message
        """
        comet.channels.send(self.channel_id, 'msg from %s: %s' % (user, msg))

@presentation.render_for(Chat)
def render(self, h, *args):
    h.head.css('nagare_chat', '''
               #msgs {
                        list-style-type: none;
                        border: 1px dashed #f3f2f1;
                        padding: 5px;
               }
               #msgs li:nth-child(odd) { background-color: #f3f2f1; }
               .msg_type_j { color: red }
               .msg_type_p { color: blue }

               ''')

    # Inclusion of the translated ``append_msg`` function
    h.head << h.head.script(ajax.py2js(append_msg, h))

    with h.div:
        # Automatic inclusion of the javascript Comet functions
        h << component.Component(comet.channels[self.channel_id])

        # Asynchronous (Ajax) rendering of the user interaction form
        h << self.interaction.render(h.AsyncRenderer())

        # This list will be filled by the received messages
        h << h.ul(id='msgs')

    return h.root

# -----------------------------------------------------------------------------

def app():
    return Chat('nagare_chat')

