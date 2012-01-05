#--
# Copyright (c) 2008-2012 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
#--

from nagare.examples.demo import Examples
from nagare.examples.wiki import wiki1, wiki2, wiki3, wiki4, wiki5, wiki6, wiki7, wiki8, wiki9

examples = (
            ('wiki1', ((wiki1.__doc__, wiki1.app),)),
            ('wiki2', ((wiki2.__doc__, wiki2.app),)),
            ('wiki3', ((wiki3.__doc__, wiki3.app),)),
            ('wiki4', ((wiki4.__doc__, wiki4.app),)),
            ('wiki5', ((wiki5.__doc__, wiki5.app),)),
            ('wiki6', ((wiki6.__doc__, wiki6.app),)),
            ('wiki7', ((wiki7.__doc__, wiki7.app),)),
            ('wiki8', ((wiki8.__doc__, wiki8.app),)),
            ('wiki9', ((wiki9.__doc__, wiki9.app),)),
           )

# TRAC url to display a module code from the Mercurial repository
HG_EXAMPLES_URL = 'http://www.nagare.org/trac/browser/examples/nagare/examples/wiki/%s.py'

app = lambda: Examples('Wiki tutorial', HG_EXAMPLES_URL, examples)
