# --
# Copyright (c) 2008-2017 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
# --

import inspect

from pygments import highlight, lexers, formatters

from nagare import presentation


class HtmlFormatter(formatters.HtmlFormatter):
    def __init__(self, active_lines, *args, **kw):
        super(HtmlFormatter, self).__init__(*args, **kw)
        self.marker_lines = {}
        self.active_lines = {}

        for i, (marker_lines, _, lines) in enumerate(active_lines):
            for marker_line in marker_lines:
                self.marker_lines[marker_line - 1] = i

            for line in lines:
                self.active_lines.setdefault(line - 1, []).append(i)

    def wrap(self, source, outfile):
        return self._wrap(source)

    def _wrap(self, source):
        for i, (code, line) in enumerate(source):
            line = line.replace('<span style="background-color: #f0f0f0; padding: 0 5px 0 5px">', '<span class="lineno">')

            if code:
                markers = self.active_lines.get(i)
                if markers is not None:
                    line = '<span class="%s">%s</span>' % (' '.join('block_%d' % marker for marker in markers), line)

                marker = self.marker_lines.get(i)
                if marker is not None:
                    line = '<span class="highlight_block_marker" name="%d">%s</span>' % (marker, line)

            yield code, line


class SourceViewer(object):
    def __init__(self, comp, mod):
        self.code = '\n'.join(line for i, line in enumerate(inspect.getsource(mod).splitlines()) if (i + 1) in mod.hl_lines[0])
        self.comp = comp
        self.hl_lines = mod.hl_lines[1:]


@presentation.render_for(SourceViewer)
def render(self, h, comp, *args):
    h.head.css_url('/static/nagare/application.css')
    h.head.css_url('portal.css')

    with h.div(id='source_viewer'):
        with h.div(class_='left'):
            h << h.a(u'\u2715', href='#', id='popup_close').action(comp.answer)

            with h.p(id='help'):
                h << 'Hold your mouse over the '
                h << h.img(src='attention_small.png')
                h << ' icons to follow the tutorial'

            with h.div(class_='comp'):
                h << self.comp.render(h.AsyncRenderer())

            for (i, (_, description, _)) in enumerate(self.hl_lines):
                h << h.div(h.parse_htmlstring(description), class_='description', id='description_%d' % i, style='display: none')

        with h.div(class_='right'):
            formatter = HtmlFormatter(self.hl_lines, nowrap=False, noclasses=True, linenos='inline')
            code = highlight(self.code, lexers.PythonLexer(), formatter)
            h << h.pre(h.parse_htmlstring(code))

        h << h.script('init_sourceviewer()')

    return h.root
