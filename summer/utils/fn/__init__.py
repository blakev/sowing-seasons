#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by: Blake on 1/3/2016 at 6:49 PM

import re

CODE_REGEX = re.compile(r'<code>[a-zA-Z]+\n', re.I)

def code_highlighter(html):
    for match in CODE_REGEX.findall(html):
        match = match.lower().strip()

        if match:
            lang = match.split('>')[-1]
            html = html.replace(match, '<code class="lang-%s">' % lang)

    return html
