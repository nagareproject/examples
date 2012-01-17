#--
# Copyright (c) 2008-2012 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
#--

VERSION='0.3.0'

from setuptools import setup, find_packages

setup(
      name = 'nagare.examples',
      version = VERSION,
      author = 'Alain Poirier',
      author_email = 'alain.poirier at net-ng.com',
      description = 'Demo and examples for the Nagare web framework',
      long_description = '''Read the `installation document <http://www.nagare.org/trac/wiki/DemoInstallation>`_
      to do a standard installation or a developer installation with the
      `latest <http://www.nagare.org/snapshots/nagare.examples-latest#egg=nagare.examples-dev>`_
      development version from the `mercurial repository <http://hg.nagare.org/examples>`_.
      ''',
      license = 'BSD',
      keywords = 'web wsgi framework sqlalchemy elixir seaside continuation ajax stackless',
      url = 'http://www.nagare.org',
      download_url = 'http://www.nagare.org/download',
      packages = find_packages(),
      include_package_data = True,
      package_data = {'' : ['*.cfg']},
      use_hg_version = True,
      zip_safe = False,
      dependency_links = ('http://www.nagare.org/download/',),
      install_requires = ('nagare[database,doc]>=0.4.0', 'PIL'),
      namespace_packages = ('nagare', 'nagare.examples',),
      entry_points = '''
      [nagare.applications]
      demo = nagare.examples.demo:app
      wiki = nagare.examples.wiki.wiki9:app
      gallery = nagare.examples.gallery.gallery7:app
      portal = nagare.examples.portal.portal:app
      jewels = nagare.examples.jewels:app
      chat = nagare.examples.chat:app
      ''',
      classifiers = (
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: BSD License',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Environment :: Web Environment',
        'Operating System :: Microsoft :: Windows :: Windows NT/2000',
        'Operating System :: Unix',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
      )
     )
