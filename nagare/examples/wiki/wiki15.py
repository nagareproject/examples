#--
# Copyright (c) 2008-2012 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
#--

"""Roles associated to the user objects

First, log as 'guest / guest'
Then, log as the editor 'john / john'.
Then try as the administrator 'admin / admin'.
"""

from __future__ import with_statement

import re
import docutils.core

from nagare import component, presentation, var, security, wsgi

from wikidata import PageData

# ---------------------------------------------------------------------------

class Login:
    pass

@presentation.render_for(Login)
def render(self, h, binding, *args):
    user = security.get_user()
    
    if not user:
        html = h.form(
                      'Login: ', h.input(name='__ac_name'), ' ',
                      'Password: ', h.input(type='password', name='__ac_password'), ' ',
                      h.input(type='submit', value='ok')
                     )
    else:
        html = (
                'Welcome ', h.b(user.id), h.br,
                h.a('logout').action(lambda: security.get_manager().logout())
               )
        
    return html

# ---------------------------------------------------------------------------

wikiwords = re.compile(r'\b([A-Z]\w+[A-Z]+\w+)')

class Page(object):
    def __init__(self, title):
        self.title = title

    def edit(self, comp):
        content = comp.call(PageEditor(self))

        if content is not None:
            security.check_permissions('wiki.editor', self)
            page = PageData.get_by(pagename=self.title)
            page.data = content

@presentation.render_for(Page)
def render(self, h, comp, *args):
    page = PageData.get_by(pagename=self.title)

    content = docutils.core.publish_parts(page.data, writer_name='html')['html_body']
    content = wikiwords.sub(r'<wiki>\1</wiki>', content)
    html = h.parse_htmlstring(content, fragment=True)[0]

    for node in html.getiterator():
        if node.tag == 'wiki':
            a = h.a(node.text, href='page/'+node.text).action(lambda title=unicode(node.text): comp.answer(title))
            node.replace(a)
    
    h << html
    
    if security.has_permissions('wiki.editor', self):
        h << h.a('Edit this page', href='page/'+self.title).action(lambda: self.edit(comp))
        
    return h.root

@presentation.render_for(Page, model='meta')
def render(self, h, comp, *args):
    return ('Viewing ', h.b(self.title), h.br, h.br,
            'You can return to the ', h.a('FrontPage', href='page/FrontPage').action(lambda: comp.answer(u'FrontPage')))

# ---------------------------------------------------------------------------

class PageEditor(object):
    def __init__(self, page):
        self.page = page

@presentation.render_for(PageEditor)
def render(self, h, comp, *args):
    content = var.Var()

    page = PageData.get_by(pagename=self.page.title)

    with h.form:
        with h.textarea(rows='10', cols='40').action(content):
            h << page.data
        h << h.br
        h << h.input(type='submit', value='Save').action(lambda: comp.answer(content()))
        h << ' '
        h << h.input(type='submit', value='Cancel').action(comp.answer)

    return h.root

@presentation.render_for(PageEditor, model='meta')
def render(self, h, *args):
    return ('Editing ', h.b(self.page.title))

# ---------------------------------------------------------------------------

class Wiki(object):
    def __init__(self):
        self.login = component.Component(Login())        
        self.content = component.Component(None)
        self.content.on_answer(self.goto)

        self.goto(u'FrontPage')

    def goto(self, title):
        page = PageData.get_by(pagename=title)
        if page is None:
            PageData(pagename=title, data='')

        self.content.becomes(Page(title))

@presentation.render_for(Wiki)
def render(self, h, comp, *args):
    h.head.css('main_css', '''
    .document:first-letter { font-size:2em }
    .meta { float:right; width: 10em; border: 1px dashed gray;padding: 1em; margin: 1em; }
    .login { font-size:0.75em; }    
    ''')

    with h.div(class_='login'):
        h << self.login

    with h.div(class_='meta'):
        h << self.content.render(h, model='meta')

    h << self.content << h.hr

    if security.has_permissions('wiki.admin', self):
        h << 'View the ' << h.a('complete list of pages', href='all').action(lambda: self.goto(comp.call(self, model='all')))
    
    return h.root

@presentation.render_for(Wiki, model='all')
@security.permissions('wiki.admin')
def render(self, h, comp, *args):
    with h.ul:
        for page in PageData.query.order_by(PageData.pagename):
            with h.li:
                h << h.a(page.pagename, href='page/'+page.pagename).action(lambda title=page.pagename: comp.answer(title))

    return h.root

# ---------------------------------------------------------------------------

@presentation.init_for(Wiki, "(len(url) == 2) and (url[0] == 'page')")
def init(self, url, *args):
    title = url[1]
    
    page = PageData.get_by(pagename=title)
    if page is None:
        raise presentation.HTTPNotFound()

    self.goto(title)
    
@presentation.init_for(Wiki, "len(url) and (url[0] == 'all')")
def init(self, url, comp, *args):
    component.call_wrapper(lambda: self.goto(comp.call(self, model='all')))

# ---------------------------------------------------------------------------

# Roles added, between the users and their permissions. Roles are a list
# of permissions and, optionally, of other roles

from peak.rules import when
from nagare.security import common

# Function to flatten roles in roles
def flatten(*args):
    return sum([flatten(*x) if hasattr(x, '__iter__') else (x,) for x in args], ())

# A user has now a list of roles
class User(common.User):
    def __init__(self, id, roles=()):
        super(User, self).__init__(id)
        self.roles = flatten(roles)
        
    def has_permission(self, permission):
        return permission in self.roles

# Predefined roles
editor_role = ('wiki.editor',)
admin_role = ('wiki.admin', editor_role)

from nagare.security import form_auth

class Authentication(form_auth.Authentication):
    def get_password(self, username):
        return username
    
    def _create_user(self, username):
        if username is None:
            return None
        
        if username == 'john':
            return User(username, editor_role)
        
        if username == 'admin':
            return User(username, admin_role)
        
        return User(username)


class UserWithRolesRules(common.Rules):
    @when(common.Rules.has_permission, (User, str))
    def _(self, user, perm, subject):
        return user.has_permission(perm)


class SecurityManager(Authentication, UserWithRolesRules):
    pass

# ---------------------------------------------------------------------------

class WSGIApp(wsgi.WSGIApp):
    def __init__(self, app_factory):
        super(WSGIApp, self).__init__(app_factory)
        self.security = SecurityManager()
        
app = WSGIApp(lambda: component.Component(Wiki()))
