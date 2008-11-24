# Copyright (C) 2008 Andi Albrecht, albrecht.andi@gmail.com
#
# This module is part of python-sqlparse and is released under
# the BSD License: http://www.opensource.org/licenses/bsd-license.php.

"""SQL parser class."""

import re

from pygments.filter import Filter
import pygments.token
from pygments.util import get_bool_opt
from pygments.lexers import SqlLexer

from dialects import Dialect, DefaultDialect


class IfFilter(Filter):
    """Marks IF as keyword."""

    def filter(self, lexer, stream):
        for ttype, value in stream:
            if ttype is pygments.token.Name and value.upper() == 'IF':
                ttype = pygments.token.Keyword
            yield ttype, value


class Parser(object):

    def __init__(self, dialect=None):
        self._dialect = None
        self._lexer = SqlLexer()
        self._lexer.add_filter(IfFilter())
        self._lexer.add_filter('whitespace')
        self.set_dialect(dialect)

    def set_dialect(self, dialect):
        """Set SQL dialect."""
        if dialect is None:
            dialect = DefaultDialect()
        assert isinstance(dialect, Dialect)
        self._dialect = dialect

    def parse(self, sql):
        """Parse sql and return list of statements."""
        tokens = []
        splitlevel = 0
        statements = []
        for tokentype, text in self._lexer.get_tokens(sql):
            tokentype, text, lvlchange = self._dialect.handle_token(tokentype,
                                                                    text)
            tokens.append((tokentype, text))
            splitlevel += lvlchange
            if not splitlevel and tokentype == pygments.token.Punctuation \
            and text == ';':
                statements.append(Statement(tokens))
                splitlevel = 0
                self._dialect.reset()
                tokens = []
        if tokens:
            statements.append(Statement(tokens))
        if statements:
            last = statements.pop()
            tokentype, text = last.tokens[-1]
            if tokentype == pygments.token.Text.Whitespace and text == '\n' \
            and not sql.endswith('\n'):  # pygments adds a \n
                last.tokens = last.tokens[:-1]
            if last.tokens:
                statements.append(last)
        return statements


class Statement(object):

    def __init__(self, tokens):
        self.tokens = tokens

    def __unicode__(self):
        return u''.join(t[1] for t in self.tokens)

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __repr__(self):
        raw = unicode(self)
        if len(raw) > 7:
            short = raw[:6]+u'...'
        else:
            short = raw
        short = re.sub('\s+', ' ', short)
        return '<Statement \'%s\' at 0x%07x>' % (short, id(self))

    def get_type(self):
        """Return statement type."""
        pass
