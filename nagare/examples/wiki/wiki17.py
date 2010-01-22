#--
# Copyright (c) 2008, 2009, 2010 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
#--

"""More complex security rules: only the author can change a page content

'guest / guest' is an editor but can't edit the 'WikiWiki' page
'john / john' is an editor and the creator of the 'WikiWiki' page so he
can edit it
Then try as the administrator 'admin / admin' that can edit all the pages
"""
from __future__ import with_statement

import re
import docutils.core

from nagare import component, presentation, var, security, wsgi, editor
from nagare.database import session, query

import wikialchemy

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
    def __init__(self, pagename):
        self.pagename = pagename
        self.data = ''
        self.creator = None

@presentation.render_for(Page)
def render(self, h, comp, *args):
    content = docutils.core.publish_parts(self.data, writer_name='html')['html_body']
    content = wikiwords.sub(r'<wiki>\1</wiki>', content)
    html = h.parse_htmlstring(content, fragment=True)[0]

    for node in html.getiterator():
        if node.tag == 'wiki':
            a = h.a(node.text, href='page/'+node.text).action(lambda title=unicode(node.text): comp.answer(title))
            node.replace(a)
    
    h << html
    
    if security.has_permissions('wiki.editor', self):
        h << h.a('Edit this page', href='page/'+self.pagename).action(lambda: comp.call(PageEditor(comp())))
        
    return h.root

# The meta data view now also displays the creator's name
@presentation.render_for(Page, model='meta')
def render(self, h, comp, *args):
    h << h.span('Viewing ') << h.b(self.pagename) << h.br

    if self.creator:
        h << h.i('Created by ', self.creator) << h.br

    h << h.br
    h << 'You can return to the ' << h.a('FrontPage', href='page/FrontPage').action(lambda: comp.answer(u'FrontPage'))

    return h.root

# ---------------------------------------------------------------------------

class PageEditor(editor.Editor):
    def __init__(self, page):
        super(PageEditor, self).__init__(page, ('pagename', 'data', 'creator'))

    #@security.permissions('wiki.editor')
    def commit(self, comp):
        if super(PageEditor, self).commit(('data',)) and self.creator.value is None:
            self.creator = security.get_user().id

        comp.answer()

@presentation.render_for(PageEditor)
def render(self, h, comp, *args):
    with h.form:
        with h.textarea(rows='10', cols='40').action(self.data):
            h << self.data()
        h << h.br
        h << h.input(type='submit', value='Save').action(lambda: self.commit(comp))
        h << ' '
        h << h.input(type='submit', value='Cancel').action(comp.answer)

    return h.root

@presentation.render_for(PageEditor, model='meta')
def render(self, h, *args):
    return ('Editing ', h.b(self.pagename()))

# ---------------------------------------------------------------------------

class Wiki(object):
    def __init__(self):
        self.login = component.Component(Login())        
        self.content = component.Component(None)
        self.content.on_answer(self.goto)

        self.goto(u'FrontPage')

    def goto(self, title):
        page = query(Page).get(title)
        if page is None:
            Page(title, '')
            session.add(Page)

        self.content.becomes(page)

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
        for page in query(Page).order_by(Page.pagename):
            with h.li:
                h << h.a(page.pagename, href='page/'+page.pagename).action(lambda title=page.pagename: comp.answer(title))

    return h.root

# ---------------------------------------------------------------------------

@presentation.init_for(Wiki, "(len(url) == 2) and (url[0] == 'page')")
def init(self, url, *args):
    title = url[1]
    
    page = query(Page).get(title)
    if page is None:
        raise presentation.HTTPNotFound()

    self.goto(title)
    
@presentation.init_for(Wiki, "len(url) and (url[0] == 'all')")
def init(self, url, comp, *args):
    component.call_wrapper(lambda: self.goto(comp.call(self, model='all')))

# ---------------------------------------------------------------------------

from peak.rules import when
from nagare.security import common

def flatten(*args):
    return sum([flatten(*x) if hasattr(x, '__iter__') else (x,) for x in args], ())

class User(common.User):
    def __init__(self, id, roles=()):
        super(User, self).__init__(id)
        self.roles = flatten(roles)
        
    def has_permission(self, permission):
        return permission in self.roles

editor_role = ('wiki.editor',)
admin_role = ('wiki.admin', editor_role)

from nagare.security import form_auth

class Authentication(form_auth.Authentication):
    def get_password(self, username):
        return username
    
    def _create_user(self, username):
        if username is None:
            return None
        
        if (username == 'john') or (username == 'guest'):
            return User(username, editor_role)
        
        if username == 'admin':
            return User(username, admin_role)
        
        return User(username)


class Rules(common.Rules):
    # A administrator has all the permissions on the Wiki
    @when(common.Rules.has_permission, (User, str, Wiki))
    def _(next_method, self, user, perm, subject):
        return user.has_permission('wiki.admin') or next_method(self, user, perm, subject)

    # 1. An administrator has all the permissions on the pages
    #
    # 2. A user can modify a page if he has the 'wiki.editor' permission
    #    and if he is the creator of the page, or if the page has no creator
    #    yet (page just created)
    @when(common.Rules.has_permission, (User, str, Page))
    def _(self, user, perm, page):
        if user.has_permission('wiki.admin'):
            return True

        creator = page.creator
        if user.has_permission(perm) and (perm != 'wiki.editor' or (creator is None) or (creator == user.id)):
            return True
        
        return common.Denial()


class SecurityManager(Authentication, Rules):
    pass

# ---------------------------------------------------------------------------

class WSGIApp(wsgi.WSGIApp):
    def __init__(self, app_factory):
        super(WSGIApp, self).__init__(app_factory)
        self.security = SecurityManager()

app = WSGIApp(lambda: component.Component(Wiki()))

# -----------------------------------------------------------------------------

from sqlalchemy.orm import Mapper

Mapper(Page, wikialchemy.page_data)

def populate():
    page = Page(u'FrontPage', u'Welcome to my *WikiWiki* !', u'admin')
    session.add(page)

    page = Page(u'WikiWiki', u'On this *WikiWiki*, the page contents can be '
                 'written in `Restructured Text <http://docutils.sourceforge.net/rst.html>`_',
                 u'john')
    session.add(page)
