# Copyright (C) 2008 Andi Albrecht, albrecht.andi@gmail.com
#
# This module is part of python-sqlparse and is released under
# the BSD License: http://www.opensource.org/licenses/bsd-license.php.

"""filter"""

import logging

from sqlparse.tokens import *

# Create our custom groups
grp = Token.Group
Group = Token.Group
grpc = Token.Group.Comment
grpl = Token.Group.Literal


class Filter(object):

    def __init__(self, **options):
        self.options = options

    def filter(self, lexer, stream):
        raise NotImplementedError


class GroupFilter(Filter):
    """Groups some elements back together."""

    def filter(self, lexer, stream):
        cached = []
        comment_in_cache = False
        for ttype, value in stream:
            if Whitespace in ttype or ttype in Comment:
                cached.append((ttype, value))
                if ttype in Comment:
                    comment_in_cache = True
                continue
            else:
                if cached and comment_in_cache:
                    new_value = ''.join(x[1] for x in cached)
                    yield Group.Comment, new_value
                elif cached:
                    for item in cached:
                        yield item
                cached = []
                comment_in_cache = False
            yield ttype, value


class UngroupFilter(Filter):

    def filter(self, lexer, stream):
        for ttype, value in stream:
            if ttype in Group:
                from parser import Parser
                # use sqlparse instead of the lexer to handle lb at the end
                p = Parser()
                for item in p.parse(value)[0].tokens:
                    yield item
            else:
                yield ttype, value


class IfFilter(Filter):
    """Marks IF as keyword."""

    def filter(self, lexer, stream):
        for ttype, value in stream:
            if ttype is Name and value.upper() == 'IF':
                ttype = Keyword
            yield ttype, value


class StripWhitespaceFilter(Filter):
    """Strips duplicate whitespaces."""

    def filter(self, lexer, stream):
        cached = []
        in_comment = False
        last = None
        for ttype, value in stream:
            if Comment in ttype.split() and not in_comment:
                in_comment = True
            if Text.Whitespace in ttype.split() \
            and value in (' ', '\t') and not in_comment:
                cached.append((ttype, value))
                continue
            if in_comment and (Comment not in ttype.split()
                               and Whitespace \
                               not in ttype.split()):
                in_comment = False
            if cached:
                yield Text.Whitespace, ' '
                cached = []
            last = (ttype, value)
            yield ttype, value


class LTrimFilter(Filter):

    def filter(self, lexer, stream):
        other_token_found = True
        for ttype, value in stream:
            if Text.Whitespace in ttype.split() \
            and value == '\n':
                other_token_found = False
            elif Text.Whitespace in ttype.split() \
            and not other_token_found:
                continue
            else:
                other_token_found = True
            yield ttype, value


class IdentifierCaseFilter(Filter):

    def __init__(self, case='lower'):
        self.case = case

    def filter(self, lexer, stream):
        for ttype, value in stream:
            if ttype is Name:
                if self.case == 'upper':
                    value = value.upper()
                elif self.case == 'capitalize':
                    value = value.capitalize()
                elif self.case == 'lower':
                    value = value.lower()
            yield ttype, value


class StripCommentsFilter(Filter):

    def filter(self, lexer, stream):
        for ttype, value in stream:
            if ttype in Group.Comment:
                continue
            yield ttype, value


class CleanupWSCommaFilter(Filter):
    """Cleanup whitespaces around comments."""

    def filter(self, lexer, stream):
        cached = []
        last_yielded = None
        for ttype, value in stream:
            if Text.Whitespace in ttype.split():
                cached.append((ttype, value))
                continue
            elif Punctuation in ttype.split() \
            and value == ',':
                if last_yielded \
                and Comment in last_yielded[0].split():
                    while cached:
                        yield cached.pop(0)
                    last_yielded = None
                else:
                    cached = []
            else:
                while cached:
                    yield cached.pop(0)
            last_yielded = (ttype, value)
            yield ttype, value


class IndentFilter(Filter):

    split_words = ('SELECT', 'FROM', 'WHERE', 'ORDER', 'JOIN', 'LIMIT',
                   'BEGIN', 'END', 'FOR', 'IF', 'LEFT', 'OUTER', 'INNER',
                   'UNION', 'GROUP', 'AND', 'OR', 'ON', 'CASE', 'WHEN',
                   'THEN', 'ELSE', 'VALUES')
    indents = {'(': (1, 0), ')': (-1, 0),
               'AND': (1, -1), 'OR': (1, -1),
               'ON': (1, -1),
               'CASE': (1, 0), 'END': (-1, 0),
               'VALUES': (1, -1)}

    def __init__(self, n_indents=2):
        self.n_indents = n_indents

    def _reindent_comment(self, comment):
        # XXX
        return comment
        new_lines = []
        for line in comment.splitlines():
            new_lines.append(line.lstrip(' \t'))
        return '\n'.join(new_lines)

    def filter(self, lexer, stream):
        wait_until_join = False
        level = 0
        for ttype, value in stream:
            before, after = self.indents.get(value.upper(), (0, 0))
            level += before
            if Keyword in ttype.split() \
            and value.upper() in self.split_words:
                if not wait_until_join:
                    yield Text.Whitespace, '\n'
                    for i in range(level):
                        for j in range(self.n_indents):
                            yield Text.Whitespace, ' '
                if value.upper() in ('LEFT', 'OUTER', 'INNER'):
                    wait_until_join = True
                elif value.upper() == 'JOIN':
                    wait_until_join = False
            elif ttype in Group.Comment:
                value = self._reindent_comment(value)
            yield ttype, value
            level += after


class RightMarginFilter(Filter):

    def __init__(self, margin):
        self.margin = margin

    def _get_line_length(self, tokens):
        return len(''.join(t[1] for t in tokens))

    def _get_indentation(self, line):
        indentation = []
        rest = []
        append_to_rest = False
        for ttype, value in line:
            if not append_to_rest \
            and Text.Whitespace in ttype.split() \
            and value in (' ', '\t'):
                indentation.append((ttype, value))
            else:
                append_to_rest = True
                rest.append((ttype, value))
        return indentation, rest

    def _split_lines(self, stream):
        line = []
        in_literal = False
        for ttype, value in stream:
            if Literal in ttype.split():
                in_literal = True
            if in_literal and Literal not in ttype.split() \
            and Text.Whitespace not in ttype.split():
                in_literal = False
            if not in_literal \
            and Text.Whitespace in ttype.split() \
            and value == '\n':
                yield line
                line = []
                in_literal = False
                continue
            line.append((ttype, value))
        if line:
            yield line

    def _fold(self, stream):
        for line in self._split_lines(stream):
            for new_line in self._fold_line(line):
                yield new_line

    def _fold_line(self, line):
        indentation, rest = self._get_indentation(line)
        new_line = []
        in_literal = False
        for ttype, value in rest:
            if new_line == []:
                new_line += indentation
            new_line.append((ttype, value))
            if Literal in ttype.split():
                in_literal = True
            if in_literal and Literal not in ttype.split() \
            and Text.Whitespace not in ttype.split():
                in_literal = False
            if not in_literal \
            and Text.Whitespace in ttype.split() \
            or (Punctuation in ttype.split() \
                and value in (';', ',', ')')):
                # TODO(andi): -10 is a dirty hack, it'd much better to have
                #  some better look ahead algorithm.
                if self._get_line_length(new_line) > self.margin-10:
                    for item in new_line:
                        yield item
                    new_line = []
                    yield Text.Whitespace, '\n'
        if new_line:
            for item in new_line:
                yield item
            yield Text.Whitespace, '\n'

    def filter(self, lexer, stream):
        for ttype, value in self._fold(stream):
            yield ttype, value


